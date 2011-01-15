from .base import Field


class String(Field):
    def __init__(self, *args, encoding=None, **kwargs):
        ''.encode(encoding)  # Check for a valid encoding
        self.encoding = encoding
        super(String, self).__init__(*args, **kwargs)

    def read(self, obj):
        # TODO: There's gotta be a better way, but it works for now
        value = b''
        while 1:
            data = obj.read(1)
            try:
                return value + data[:data.index(b'\x00')]
            except ValueError:
                value += data

    def encode(self, value):
        return value.encode(self.encoding)

    def decode(self, value):
        return value.decode(self.encoding)


class FixedString(String):
    def __init__(self, value, *args, encoding='ascii', **kwargs):
        super(FixedString, self).__init__(*args, encoding=encoding, size=None, **kwargs)
        if isinstance(value, bytes):
            # If raw bytes are supplied, encoding is not used
            self.encoded_value = value
            self.decoded_value = value
            self.encoding = None
        elif isinstance(value, str):
            self.decoded_value = value
            self.encoded_value = super(FixedString, self).encode(value)
        self.size = len(self.encoded_value)

    def encode(self, value):
        if value != self.decoded_value:
            raise ValueError('Expected %r, got %r.' % (self.decoded_value, value))
        return self.encoded_value

    def decode(self, value):
        if value != self.encoded_value:
            raise ValueError('Expected %r, got %r.' % (self.encoded_value, value))
        return self.decoded_value


class Bytes(Field):
    def __init__(self, *args, **kwargs):
        super(Bytes, self).__init__(*args, **kwargs)
        if not self.size:
            raise TypeError("Size is required for Bytes fields")

    def encode(self, value):
        # Nothing to do here
        return value

    def decode(self, value):
        # Nothing to do here
        return value


