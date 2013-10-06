import collections
import io

from steel.common import meta, fields

__all__ = ['Structure', 'StructureStreamer', 'StructureTuple']


class StructureBase:
    def __init__(self, *args, **kwargs):
        self._file = len(args) > 0 and args[0] or None
        self._mode = self._file and 'rb' or 'wb'
        self._position = 0
        self._write_buffer = b''
        self._raw_values = {}
        self._parent = None

        if self._file and kwargs:
            raise TypeError("Cannot supply a file and attributes together")

        for name, value in kwargs.items():
            setattr(self, name, value)

    def read(self, size=None):
        if self._mode != 'rb':
            raise IOError("not readable")
        if size is None:
            return self._file.read()
        value = self._file.read(size)
        self._position += len(value)
        return value

    def write(self, data):
        if self._mode != 'wb':
            raise IOError("not writable")
        file = EOFBytesIO(self._write_buffer + data)
        last_position = 0
        for name, field in self.__class__._fields.items():
            if name not in self.__dict__:
                try:
                    try:
                        bytes = field.read(file)
                        value = field.decode(bytes)
                    except fields.FullyDecoded as obj:
                        bytes = obj.bytes
                        value = obj.value
                    self._raw_values[name] = bytes
                    self.__dict__[name] = value
                    last_position = file.tell()
                except EOFError:
                    file.seek(last_position)
                    self._write_buffer = file.read()
                else:
                    self._write_buffer = b''
        self._position += last_position

    def tell(self):
        return self._position

    def _extract(self, field):
        if field.name not in self._raw_values:
            for name, other_field in self._fields.items():
                if name not in self._raw_values:
                    with other_field.for_instance(self):
                        try:
                            bytes = other_field.read(self)
                        except fields.FullyDecoded as obj:
                            bytes = obj.bytes
                            self.__dict__[name] = obj.value
                        self._raw_values[name] = bytes
                if name == field.name:
                    break
        return self._raw_values[field.name]

    def get_raw_bytes(self):
        output = b''
        for name, field in self.__class__._fields.items():
            value = getattr(self, name)
            if name not in self._raw_values:
                setattr(self, name, getattr(self, name))
            output += self._raw_values[name]
        return output

    def get_parent(self):
        if isinstance(self._parent, Structure):
            return self._parent
        raise TypeError('%s has no parent' % self.__class__.__name__)

    def save(self, file):
        file.write(self.get_raw_bytes())

    def dump(self, file):
        file.write(self.dumps())

    def dumps(self):
        return self.get_raw_bytes()

    def validate(self):
        errors = []
        for name, field in self._fields.items():
            try:
                field.validate(self, getattr(self, name))
            except ValueError as error:
                errors.append(str(error))
        return errors

    def __str__(self):
        return '<Binary Data>'

    def __repr__(self):
        return '<%s: %s>' % (type(self).__name__, self)


class Structure(StructureBase, metaclass=meta.DeclarativeMetaclass):
    pass


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


class StructureStreamer:
    def __init__(self, structure):
        self.structure = structure

    def parse(self, file):
        while 1:
            position = file.tell()
            try:
                value = self.structure(file)
                for name, field in self.structure._fields.items():
                    getattr(value, name)
            except Exception as e:
                if file.tell() == position:
                    # The file didn't move, so it must be at the end
                    break
                # Otherwise, something else went wrong
                raise e
            yield value


class StructureTupleMetaclass(meta.DeclarativeMetaclass):
    def __init__(cls, name, bases, attrs, **options):
        super(StructureTupleMetaclass, cls).__init__(name, bases, attrs, **options)
        cls._namedtuple = collections.namedtuple(name, cls._fields.keys())


class StructureTuple(StructureBase, metaclass=StructureTupleMetaclass):
    def __new__(cls, *args, **kwargs):
        self._file = len(args) > 0 and args[0] or None
        self._mode = self._file and 'rb' or 'wb'
        self._position = 0
        self._write_buffer = b''
        self._raw_values = {}
        self._parent = None

        if self._file and kwargs:
            raise TypeError("Cannot supply a file and attributes together")

        data = (kwargs.get(name, None) for name in cls._fields)
        return cls._namedtuple(*data)

    def __init__(self, structure, *args, **kwargs):
        super(StructureTuple, self).__init__(structure, *args, **kwargs)
        self.names = [name for name in self.structure._fields if not name.startswith('_')]
        self.namedtuple = collections.namedtuple(structure.__name__, ' '.join(self.names))

    def read(self, file):
        try:
            raw_bytes = super(StructureTuple, self).read(file)
            value = self.decode(bytes)
        except FullyDecoded as obj:
            raw_bytes = obj.bytes
            value = obj.value
        values = []
        value = self.namedtuple(*(getattr(value, name) for name in self.names))

        raise FullyDecoded(raw_bytes, value)
