from .base import Field


# Endianness options

class BigEndian:
    def __init__(self, size):
        self.size = size

    def encode(self, value):
        return bytes((value >> (self.size - i - 1) * 8) & 0xff for i in range(self.size))

    def decode(self, value):
        return sum(v * 0x100 ** (self.size - i - 1) for i, v in enumerate(value[:self.size]))


class LittleEndian:
    def __init__(self, size):
        self.size = size

    def encode(self, value):
        return bytes((value >> i * 8) & 0xff for i in range(self.size))

    def decode(self, value):
        return sum(v * 0x100 ** i for i, v in enumerate(value[:self.size]))


# Signed Number Representations

class SignMagnitude:
    def __init__(self, size):
        self.size = size

    def encode(self, value):
        if value > (1 << (self.size * 8)) - 1:
            raise ValueError("Value is too large to encode.")
        if value < 0:
            # Set the sign to negative
            return -value | (1 << (self.size * 8 - 1))
        return value

    def decode(self, value):
        if value >> (self.size * 8 - 1):
            # The sign is negative
            return -(value ^ (2 ** (self.size * 8 - 1)))
        return value


class OnesComplement:
    def __init__(self, size):
        self.size = size

    def encode(self, value):
        if value > (1 << (self.size * 8)) - 1:
            raise ValueError("Value is too large to encode.")
        if value < 0:
            # Value is negative
            return ~(-value) & (2 ** (self.size * 8) - 1)
        return value

    def decode(self, value):
        if value >> (self.size * 8 - 1):
            # Value is negative
            return -(~value & (2 ** (self.size * 8) - 1))
        return value


class TwosComplement:
    def __init__(self, size):
        self.size = size

    def encode(self, value):
        if value > (1 << (self.size * 8 - 1)) - 1:
            raise ValueError("Value is too large to encode.")
        if value < 0:
            # Value is negative
            return (~(-value) & (2 ** (self.size * 8) - 1)) + 1
        return value

    def decode(self, value):
        if value > 2 ** (self.size * 8 - 1) - 1:
            # Value is negative
            return -(~value & (2 ** (self.size * 8) - 1)) - 1
        return value


# Numeric types

class Integer(Field):
    def __init__(self, *args, signed=True, endianness=BigEndian,
                 signing=TwosComplement, **kwargs):
        super(Integer, self).__init__(*args, **kwargs)
        self.endianness = endianness(self.size)
        self.signed = signed
        self.signing = signing(self.size)

    def attach_to_class(self, cls, name, endianness=BigEndian,
                        signing=TwosComplement, **options):
        super(Integer, self).attach_to_class(cls, name, **options)

    def encode(self, value):
        if self.signed:
            value = self.signing.encode(value)
        elif value < 0:
            raise ValueError("Value cannot be negative.")
        if value > (1 << (self.size * 8)) - 1:
            raise ValueError("Value is large for this field.")
        return self.endianness.encode(value)

    def decode(self, value):
        value = self.endianness.decode(value)
        if self.signed:
            value = self.signing.decode(value)
        return value


class FixedInteger(Integer):
    def __init__(self, value, *args, **kwargs):
        super(FixedInteger, self).__init__(*args, signed=value < 0, **kwargs)
        if not self.size:
            raise TypeError("Size is required for fixed integers")
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


class PositiveInteger(Integer):
    def __init__(self, *args, signed=False, **kwargs):
        super(PositiveInteger, self).__init__(*args, signed=signed, **kwargs)


class Byte(Integer):
    def __init__(self, *args, size=1, **kwargs):
        super(Byte, self).__init__(*args, size=size, **kwargs)


