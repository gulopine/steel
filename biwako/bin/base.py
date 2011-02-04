import collections
import io

from ..bin import data


class NameAwareOrderedDict(collections.OrderedDict):
    """
    A custom namespace that not only orders its items, but can
    also make those items aware of their names immediately.
    """

    def __setitem__(self, name, obj):
        super(NameAwareOrderedDict, self).__setitem__(name, obj)
        if hasattr(obj, 'set_name'):
            obj.set_name(name)


class StructureMeta(type):
    def __new__(cls, name, bases, attrs, **options):
        # Nothing to do here, but we need to make sure options
        # don't get passed in to type.__new__() itself.
        return type.__new__(cls, name, bases, attrs)

    def __init__(cls, name, bases, attrs, **options):
        cls._fields = []
        for name, attr in attrs.items():
            if hasattr(attr, 'attach_to_class'):
                attr.attach_to_class(cls)
        data.fields.options = {}

    @classmethod
    def __prepare__(metacls, name, bases, **options):
        data.fields.options = options
        return NameAwareOrderedDict()

    def __iter__(cls):
        return iter(cls.__dict__)

class Structure(metaclass=StructureMeta):
    def __init__(self, *args, **kwargs):
        self._file = len(args) > 0 and args[0] or None
        self._mode = self._file and 'rb' or 'wb'
        self._position = 0
        self._write_buffer = b''

        if self._file and kwargs:
            raise TypeError("Cannot supply a file and attributes together")

        for name, value in kwargs.items():
            setattr(self, name, value)

    def read(self, size=None):
        if self._mode != 'rb':
            raise IOError("not readable")
        if size is None:
            return self._file.read()
        return self._file.read(size)

    def write(self, data):
        if self._mode != 'wb':
            raise IOError("not writable")
        file = EOFBytesIO(self._write_buffer + data)
        last_position = 0
        for field in self.__class__._fields:
            if field.name not in self.__dict__:
                try:
                    self.__dict__[field.name] = field.extract(file)
                    last_position = file.tell()
                except EOFError:
                    file.seek(last_position)
                    self._write_buffer = file.read()
                else:
                    self._write_buffer = b''

    def _get_value(self, field):
        if field.name not in self.__dict__:
            if field.offset is not None and hasattr(self, 'seek'):
                self.seek(field.offset)
                self.__dict__[field.name] = field.extract(self)
            else:
                for other_field in self.__class__._fields:
                    if other_field.name not in self.__dict__:
                        self.__dict__[other_field.name] = other_field.extract(self)
                    if other_field.name == field.name:
                        break
        if field is getattr(self.__class__, field.name):
            return self.__dict__[field.name]
        return field.extract(self)

    def save(self, file):
        for field in self.__class__._fields:
            value = getattr(self, field.name)
            file.write(field.encode(self, value))

    def validate(self):
        errors = []
        for field in self._fields:
            try:
                field.validate(getattr(self, field.name))
            except ValueError as error:
                errors.append(str(error))
        return errors

    def __str__(self):
        return '<Binary Data>'

    def __repr__(self):
        return '<%s: %s>' % (type(self).__name__, self)


class EOFBytesIO(io.BytesIO):
    """
    A customized BytesIO that raises an EOFError if more data was requested
    than is available in the data stream.
    """
    def read(self, size=None):
        data = super(EOFBytesIO, self).read(size)
        if size is not None and len(data) < size:
            raise EOFError
        return data


