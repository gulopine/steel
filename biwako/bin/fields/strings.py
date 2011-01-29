from .base import Field, DynamicValue
from .numbers import Integer


class String(Field):
    def __init__(self, *args, encoding, padding=b'\x00',
                 terminator=b'\x00', **kwargs):
        ''.encode(encoding)  # Check for a valid encoding
        self.encoding = DynamicValue(encoding)
        self.padding = padding
        self.terminator = terminator
        super(String, self).__init__(*args, **kwargs)

    def extract(self, obj):
        size = self.size(obj)

        if size is not None:
            value = obj.read(size).rstrip(self.padding)

        else:
        # TODO: There's gotta be a better way, but it works for now
            value = b''
            while True:
                data = obj.read(1)
                if data == self.terminator:
                    break
                value += data

        return value.decode(self.encoding(obj))

    def encode(self, obj, value):
        value = value.encode(self.encoding(obj))
        size = self.size(obj)
        if size is not None:
            if len(value) > size:
                raise ValueError("String %r too is longer than %r bytes." % (value, size))
            value = value.ljust(size, self.padding)
        else:
            value += self.terminator
        return value


class LengthIndexedString(String):
    def extract(self, obj):
        length_field = Integer(size=self.size(obj))
        length = length_field.extract(obj)
        value = obj.read(length)
        return value.decode(self.encoding(obj))

    def encode(self, obj, value):
        length_field = Integer(size=self.size(obj))
        content = value.encode(self.encoding(obj))
        length = length_field.encode(obj, len(content))
        return length + content


class FixedString(String):
    def __init__(self, value, *args, encoding='ascii', **kwargs):
        super(FixedString, self).__init__(*args, encoding=encoding, size=None,
                                          padding=b'', terminator=b'', **kwargs)
        if isinstance(value, bytes):
            # If raw bytes are supplied, encoding is not used
            self.encoded_value = value
            self.decoded_value = value
            self.encoding = None
        elif isinstance(value, str):
            self.decoded_value = value
            self.encoded_value = super(FixedString, self).encode(None, value)
        self.size = DynamicValue(len(self.encoded_value))

    def extract(self, obj):
        value = obj.read(self.size(obj))
        if value != self.encoded_value:
            raise ValueError('Expected %r, got %r.' % (self.encoded_value, value))
        return self.decoded_value

    def encode(self, obj, value):
        if value != self.decoded_value:
            raise ValueError('Expected %r, got %r.' % (self.decoded_value, value))
        return self.encoded_value


class Bytes(Field):
    def __init__(self, *args, **kwargs):
        super(Bytes, self).__init__(*args, **kwargs)
        if not self.size:
            raise TypeError("Size is required for Bytes fields")

    def encode(self, obj, value):
        # Nothing to do here
        return value

    def decode(self, value):
        # Nothing to do here
        return value


