import collections
from .fields.base import FieldMeta

class StructureMeta(type):
    def __new__(cls, name, bases, attrs, **options):
        # Nothing to do here, but we need to make sure options
        # don't get passed in to type.__new__() itself.
        return type.__new__(cls, name, bases, attrs)

    def __init__(cls, name, bases, attrs, **options):
        cls._fields = []
        for name, attr in attrs.items():
            if hasattr(attr, 'attach_to_class'):
                attr.attach_to_class(cls, name, **options)
        FieldMeta._registry.options = {}

    @classmethod
    def __prepare__(metacls, name, bases, **options):
        FieldMeta._registry.options = options
        return collections.OrderedDict()

    def __iter__(cls):
        return iter(cls.__dict__)

class Structure(metaclass=StructureMeta):
    def __init__(self, *args, **kwargs):
        self._file = len(args) > 0 and args[0] or None
        self._mode = self._file and 'rb' or 'wb'
        self._position = 0
        self._raw_values = {}

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
        pass

    def _get_value(self, field):
        if field.offset is not None and hasattr(self, 'seek'):
            self.seek(field.offset)
            self._raw_values[field.name] = field.read(self)
        else:
            for other_field in self.__class__._fields:
                if other_field.name not in self._raw_values:
                    self._raw_values[other_field.name] = other_field.read(self)
                if other_field is field:
                    break
        return field.decode(self._raw_values[field.name])


