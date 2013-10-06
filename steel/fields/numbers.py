import decimal

from steel.fields import Field
from steel.common import args, fields

__all__ = ['BigEndian', 'LittleEndian', 'SignMagnitude', 'OnesComplement',
           'TwosComplement', 'Integer', 'FixedInteger', 'FixedPoint',
           'CalculatedValue']


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
        if value > (1 << self.size) - 1:
            raise ValueError("Value is too large to encode.")
        if value < 0:
            # Set the sign to negative
            return -value | (1 << (self.size - 1))
        return value

    def decode(self, value):
        if value >> (self.size - 1):
            # The sign is negative
            return -(value ^ (2 ** (self.size - 1)))
        return value


class OnesComplement:
    def __init__(self, size):
        self.size = size

    def encode(self, value):
        if value > (1 << self.size) - 1:
            raise ValueError("Value is too large to encode.")
        if value < 0:
            # Value is negative
            return ~(-value) & (2 ** self.size - 1)
        return value

    def decode(self, value):
        if value >> (self.size - 1):
            # Value is negative
            return -(~value & (2 ** self.size - 1))
        return value


class TwosComplement:
    def __init__(self, size):
        self.size = size

    def encode(self, value):
        if value > (1 << (self.size - 1)) - 1:
            raise ValueError("Value is too large to encode.")
        if value < 0:
            # Value is negative
            return (~(-value) & (2 ** self.size - 1)) + 1
        return value

    def decode(self, value):
        if value > 2 ** (self.size - 1) - 1:
            # Value is negative
            return -(~value & (2 ** self.size - 1)) - 1
        return value


# Numeric types

class Integer(Field):
    size = args.Override(resolve_field=False)

    signed = args.Argument(default=False)
    endianness = args.Argument(default=BigEndian)
    signing = args.Argument(default=TwosComplement)

    @signing.init
    def init_signing(self, value):
        return value(self.size * 8)

    @endianness.init
    def init_endianness(self, value):
        return value(self.size)

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

    def __lshift__(self, other):
        return CalculatedValue(self, other, lambda a, b: a << b)

    def __rlshift__(self, other):
        return CalculatedValue(self, other, lambda a, b: b << a)

    def __rshift__(self, other):
        return CalculatedValue(self, other, lambda a, b: a >> b)

    def __rrshift__(self, other):
        return CalculatedValue(self, other, lambda a, b: b >> a)

    def __lt__(self, other):
        return fields.Condition(self, other, lambda a, b: a < b)

    def __lte__(self, other):
        return fields.Condition(self, other, lambda a, b: a <= b)

    def __gte__(self, other):
        return fields.Condition(self, other, lambda a, b: a >= b)

    def __gt__(self, other):
        return fields.Condition(self, other, lambda a, b: a > b)


class FixedInteger(Integer):
    def __init__(self, value, *args, size=None, **kwargs):
        if size is None:
            size = int((value.bit_length() + 7) / 8) or 1
        super(FixedInteger, self).__init__(*args, size=size, signed=value < 0, **kwargs)
        self.decoded_value = value
        self.encoded_value = super(FixedInteger, self).encode(value)
        self.default = self.encoded_value

    def encode(self, value):
        if value != self.decoded_value:
            raise ValueError('Expected %r, got %r.' % (self.decoded_value, value))
        return self.encoded_value

    def decode(self, value):
        if value != self.encoded_value:
            raise ValueError('Expected %r, got %r.' % (self.encoded_value, value))
        return self.decoded_value


class FixedPoint(Integer):
    def __init__(self, *args, decimal_places, **kwargs):
        super(FixedPoint, self).__init__(*args, **kwargs)
        self.decimal_places = decimal_places

    def encode(self, value):
        factor = 10 ** self.decimal_places
        value = round(value * self._factor)
        return super(FixedPoint, self).encode(value)

    def decode(self, value):
        factor = 10 ** self.decimal_places
        value = super(FixedPoint, self).decode(value)
        return decimal.Decimal('%d.%d' % (value // factor, value % factor))


class CalculatedValue(Integer):
    def __init__(self, field, other, calculate, **kwargs):
        super(CalculatedValue, self).__init__(size=field.size, **kwargs)
        self.field = field
        self._parent = field._parent
        if isinstance(other, Field) and self.instance:
            other = getattr(self.instance, other.name)
        self.other = other
        self.calculate = calculate
        if hasattr(field, 'name'):
            self.set_name(field.name)

    def read(self, file):
        # Defer to the stored field in order to get a base value
        with self.for_instance(self.instance):
            return self.field.read(file)

    def encode(self, value):
        return self.field.encode(value)

    def decode(self, value):
        return self.calculate(self.field.decode(value), self.other)

    def resolve(self, value):
        if hasattr(self.field, 'name'):
            resolved_value = self.field.resolve(value)
        else:
            return super(CalculatedValue, self).resolve(value)

        resolved_other = self.other
        if hasattr(self.other, 'resolve'):
            resolved_other = self.other.resolve(value)

        return self.calculate(resolved_value, resolved_other)


