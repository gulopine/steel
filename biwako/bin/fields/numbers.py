from .base import Field


# Endianness options

class BigEndian:
    def encode(self, value, size):
        return bytes((value >> i * 8) & 0xff for i in range(size))

    def decode(self, value, size):
        return sum(v * 0x100 ** (size - i - 1) for i, v in enumerate(value[:size]))


class LittleEndian:
    def encode(self, value, size):
        return bytes((value >> (size - i - 1) * 8) & 0xff for i in range(size))

    def decode(self, value, size):
        return sum(v * 0x100 ** i for i, v in enumerate(value[:size]))


# Numeric types

class Integer(Field):
    def __init__(self, *args, signed=True, endianness=BigEndian, **kwargs):
        self.endianness = endianness
        self.signed = signed
        super(Integer, self).__init__(*args, **kwargs)

    def encode(self, value):
        return self.endianness.encode(value, self.size)

    def decode(self, value):
        return self.endianness.decode(value, self.size)


class PositiveInteger(Integer):
    def __init__(self, *args, signed=False, **kwargs):
        super(PositiveInteger, self).__init__(*args, signed=signed, **kwargs)


class Byte(Integer):
    def __init__(self, *args, size=1, **kwargs):
        super(Byte, self).__init__(*args, size=size, **kwargs)


