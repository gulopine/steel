from steel.fields import Field
from steel.fields.numbers import Integer
from steel.common import args
from steel.common.fields import FullyDecoded


class String(Field):
    size = args.Override(default=None)
    encoding = args.Argument(resolve_field=True)
    padding = args.Argument(default=b'\x00')
    terminator = args.Argument(default=b'\x00')

    def read(self, file):
        if self.size is not None:
            return file.read(self.size)

        else:
            # TODO: There's gotta be a better way, but it works for now
            value = b''
            while True:
                data = file.read(1)
                if data:
                    value += data
                    if data == self.terminator:
                        break
                else:
                    break

        return value

    def decode(self, value):
        return value.rstrip(self.terminator).rstrip(self.padding).decode(self.encoding)

    def encode(self, value):
        value = value.encode(self.encoding)
        if self.size is not None:
            value = value.ljust(self.size, self.padding)
        else:
            value += self.terminator
        return value

    def validate(self, obj, value):
        value = value.encode(self.encoding)
        if self.size is not None:
            if len(value) > self.size:
                raise ValueError("String %r is longer than %r bytes." % (value, self.size))


class LengthIndexedString(String):
    def read(self, file):
        size_bytes, size = Integer(size=self.size).read_value(file)
        value_bytes = file.read(size)
        return size_bytes + value_bytes

    def decode(self, value):
        # Skip the length portion of the byte string before decoding
        return value[self.size:].decode(self.encoding)

    def encode(self, value):
        value_bytes = value.encode(self.encoding)
        size_bytes = Integer(size=self.size).encode(len(value_bytes))
        return size_bytes + value_bytes


class FixedString(String):
    size = args.Override(default=None)
    encoding = args.Override(default='ascii')
    padding = args.Override(default=b'')
    terminator = args.Override(default=b'')

    def __init__(self, value, *args, **kwargs):
        super(FixedString, self).__init__(*args, **kwargs)

        if isinstance(value, bytes):
            # If raw bytes are supplied, encoding is not used
            self.encoded_value = value
            self.decoded_value = value
            self.encoding = None
        elif isinstance(value, str):
            self.decoded_value = value
            self.encoded_value = super(FixedString, self).encode(value)
        self.size = len(self.encoded_value)
        self.default = self.encoded_value

    def read(self, file):
        value = file.read(self.size)

        # Make sure to validate the string, even if it's not explicitly accessed.
        # This will prevent invalid files from being read beyond the fixed string.
        if value != self.encoded_value:
            raise ValueError('Expected %r, got %r.' % (self.encoded_value, value))

        raise FullyDecoded(self.encoded_value, self.decoded_value)

    def decode(self, value):
        if value != self.encoded_value:
            raise ValueError('Expected %r, got %r.' % (self.encoded_value, value))
        return self.decoded_value

    def encode(self, value):
        if value != self.decoded_value:
            raise ValueError('Expected %r, got %r.' % (self.decoded_value, value))
        return self.encoded_value


class Bytes(Field):
    def encode(self, value):
        # Nothing to do here
        return value

    def decode(self, value):
        # Nothing to do here
        return value


