from .base import Field, DynamicValue, FullyDecoded


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
    def __init__(self, *args, size, signed=False, endianness=BigEndian,
                 signing=TwosComplement, **kwargs):
        super(Integer, self).__init__(*args, size=size, **kwargs)
        self.endianness = endianness(size)
        self.signed = signed
        self.signing = signing(size)

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
        return CalculatedValue(self, other, lambda a, b: a + b)
    __radd__ = __add__

    def __sub__(self, other):
        return CalculatedValue(self, other, lambda a, b: a - b)

    def __rsub__(self, other):
        return CalculatedValue(self, other, lambda a, b: b - a)

    def __mul__(self, other):
        return CalculatedValue(self, other, lambda a, b: a * b)
    __rmul__ = __mul__

    def __pow__(self, other):
        return CalculatedValue(self, other, lambda a, b: a ** b)

    def __rpow__(self, other):
        return CalculatedValue(self, other, lambda a, b: b ** a)

    def __truediv__(self, other):
        return CalculatedValue(self, other, lambda a, b: a / b)

    def __rtruediv__(self, other):
        return CalculatedValue(self, other, lambda a, b: b / a)

    def __floordiv__(self, other):
        return CalculatedValue(self, other, lambda a, b: a // b)

    def __rfloordiv__(self, other):
        return CalculatedValue(self, other, lambda a, b: b // a)

    def __divmod__(self, other):
        return CalculatedValue(self, other, lambda a, b: divmod(a, b))

    def __rdivmod__(self, other):
        return CalculatedValue(self, other, lambda a, b: divmod(b, a))

    def __and__(self, other):
        return CalculatedValue(self, other, lambda a, b: a & b)
    __rand__ = __and__

    def __or__(self, other):
        return CalculatedValue(self, other, lambda a, b: a | b)
    __ror__ = __or__

    def __xor__(self, other):
        return CalculatedValue(self, other, lambda a, b: a ^ b)
    __rxor__ = __xor__


class FixedInteger(Integer):
    def __init__(self, value, *args, size=None, **kwargs):
        if size is None:
            size = int((value.bit_length() + 7) / 8) or 1
        super(FixedInteger, self).__init__(*args, size=size, signed=value < 0, **kwargs)
        self.size = self.size.value
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
    def __init__(self, field, other, calculate, **kwargs):
        super(CalculatedValue, self).__init__(size=field.size, **kwargs)
        self.field = field
        self.other = DynamicValue(other)
        self.calculate = calculate
        self.set_name(field.name)

    def read(self, file):
        # Defer to the stored field in order to get a base value
        field = self.field.for_instance(self.instance)
        bytes, value = field.read_value(file)
        raise FullyDecoded(b'', self.calculate(value, self.other))


