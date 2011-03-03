import io

from biwako import common
from .fields import FullyDecoded


class Structure(metaclass=common.DeclarativeMetaclass):
    def __init__(self, *args, **kwargs):
        self._file = len(args) > 0 and args[0] or None
        self._mode = self._file and 'rb' or 'wb'
        self._position = 0
        self._write_buffer = b''
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
            for other_field in self.__class__._fields:
                if other_field.name not in self.__dict__:
                    self.__dict__[other_field.name] = other_field.extract(self)
                if other_field.name == field.name:
                    break
        if field is getattr(self.__class__, field.name):
            return self.__dict__[field.name]
        return field.extract(self)

    def _extract(self, field):
        if field.name not in self._raw_values:
            for other_field in self._fields:
                if other_field.name not in self._raw_values:
                    instance_field = other_field.for_instance(self)
                    try:
                        bytes = instance_field.read(self)
                    except FullyDecoded as obj:
                        bytes = obj.bytes
                        self.__dict__[other_field.name] = obj.value
                    self._raw_values[instance_field.name] = bytes
                if other_field.name == field.name:
                    break
        return self._raw_values[field.name]

    def save(self, file):
        for field in self.__class__._fields:
            value = getattr(self, field.name)
            if field.name not in self._raw_values:
                setattr(self, field.name, getattr(self, field.name))
            file.write(self._raw_values[field.name])

    def validate(self):
        errors = []
        for field in self._fields:
            try:
                field.validate(self, getattr(self, field.name))
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


