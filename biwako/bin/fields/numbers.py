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
    def __init__(self, *args, signed=False, endianness=BigEndian,
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

    def __add__(self, other):
        return CalculatedValue(self, lambda x: x + other)
    __radd__ = __add__

    def __sub__(self, other):
        return CalculatedValue(self, lambda x: x - other)

    def __rsub__(self, other):
        return CalculatedValue(self, lambda x: other - x)

    def __mul__(self, other):
        return CalculatedValue(self, lambda x: x * other)
    __rmul__ = __mul__

    def __pow__(self, other):
        return CalculatedValue(self, lambda x: x ** other)

    def __rpow__(self, other):
        return CalculatedValue(self, lambda x: other ** x)

    def __truediv__(self, other):
        return CalculatedValue(self, lambda x: x / other)

    def __rtruediv__(self, other):
        return CalculatedValue(self, lambda x: other / x)

    def __floordiv__(self, other):
        return CalculatedValue(self, lambda x: x // other)

    def __rfloordiv__(self, other):
        return CalculatedValue(self, lambda x: other // x)

    def __divmod__(self, other):
        return CalculatedValue(self, lambda x: divmod(x, other))

    def __rdivmod__(self, other):
        return CalculatedValue(self, lambda x: divmod(other, x))

    def __and__(self, other):
        return CalculatedValue(self, lambda x: other & x)
    __rand__ = __and__

    def __or__(self, other):
        return CalculatedValue(self, lambda x: other | x)
    __ror__ = __or__

    def __xor__(self, other):
        return CalculatedValue(self, lambda x: other ^ x)
    __rxor__ = __xor__


class FixedInteger(Integer):
    def __init__(self, value, *args, size=None, **kwargs):
        if size is None:
            size = int((value.bit_length() + 7) / 8) or 1
        super(FixedInteger, self).__init__(*args, size=size, signed=value < 0, **kwargs)
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


class CalculatedValue(Integer):
    def __init__(self, field, calculate=(lambda x: x)):
        self.field = field
#        self.name = field.name
        self.calculate = calculate

    def read(self, obj):
        # Defer to the stored field in order to get a base value
        return self.field.read(obj)

    def decode(self, value):
        value = self.field.decode(value)
        return self.calculate(value)


