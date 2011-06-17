import sys
import builtins

from biwako import bin, args


class Structure(bin.Structure):
    def __init__(self, *args, **kwargs):
        super(Structure, self).__init__(*args, **kwargs)
        self._bits_left = 0
        self._bit_buffer = 0

    def read(self, size=None):
        bit_buffer = self._bit_buffer
        if size > self._bits_left:
            # Read more bytes from the file
            read_size = int(((size - self._bits_left) + 7) / 8)
            field = bin.Integer(size=read_size)
            bytes = self._file.read(read_size)
            value = field.decode(bytes)
            bit_buffer = (bit_buffer << size) | value
            self._bits_left += read_size * 8
        self._bits_left -= size % 8
        bits = bit_buffer >> self._bits_left
        self._bit_buffer = bit_buffer & (1 << self._bits_left) - 1
        return bits

    def get_raw_bytes(self):
        output = bytearray()
        bits_read = 0
        byte = 0
        for field in self.__class__._fields:
            if field.name not in self._raw_values:
                setattr(self, field.name, getattr(self, field.name))
            bits_read += field.size
            bits = self._raw_values[field.name]
            byte = (byte << field.size) + bits
            while bits_read >= 8:
                byte >>= 8
                output.append(byte & 0xFF)
                bits_read -= 8
        return bytes(output)


class Field(bin.Field):
    size = args.Argument(resolve_field=True)
    choices = args.Argument(default=())
    default = args.Argument(default=args.NotProvided)

    def __init__(self, label='', **kwargs):
        self.label = label

        for name, arg in self.arguments.items():
            if name in kwargs:
                value = kwargs.pop(name)
            elif arg.has_default:
                value = arg.default
            else:
                raise TypeError("The %s argument is required for %s fields" % (arg.name, self.__class__.__name__))
            setattr(self, name, value)
        if kwargs:
            raise TypeError("%s is not a valid argument for %s fields" % (list(kwargs.keys())[0], self.__class__.__name__))

        # Once the base values are all in place, arguments can be initialized properly
        for name, arg in self.arguments.items():
            setattr(self, name, arg.initialize(self, getattr(self, name)))


class Integer(bin.Integer):
    size = args.Override(resolve_field=False)
    signed = args.Argument(default=False)

    def encode(self, value):
        if value > (1 << self.size) - 1:
            raise ValueError("Value is large for this field.")
        return value & ((1 << self.size) - 1)

    def decode(self, value):
        if value > (1 << self.size) - 1:
            raise ValueError("Value is large for this field.")
        return value & ((1 << self.size) - 1)


class FixedInteger(Integer):
    def __init__(self, value, *args, **kwargs):
        super(FixedInteger, self).__init__(*args, signed=value < 0, **kwargs)
        self.decoded_value = value
        self.encoded_value = super(FixedInteger, self).encode(value)

    def encode(self, value):
        if value != self.decoded_value:
            raise ValueError('Expected %r, got %r.' % (self.decoded_value, value))
        return self.encoded_value

    def decode(self, value):
        if value != self.encoded_value:
            raise ValueError('Expected %r, got %r.' % (self.encoded_value, value))
        return self.decoded_value


class Flag(Integer):
    size = args.Override(default=1)

    def encode(self, value):
        return int(super(Flag, self).encode(value))

    def decode(self, value):
        return bool(super(Flag, self).decode(value))


class Reserved(bin.Reserved):
    def encode(self, value):
        return 0


