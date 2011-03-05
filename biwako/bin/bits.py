from biwako import bin
from ..common import DeclarativeMetaclass
from .fields import args


class BitStructureMetaclass(bin.DeclarativeMetaclass):
    @classmethod
    def __prepare__(cls, name, bases, **options):
        return super(BitStructureMetaclass, cls).__prepare__(name, bases, **options)


#bits_left = 0
#
#struct.read(5)
#super.read(1)
#bits_left = 3
#
#struct.read(5)
#super.read(1)
#bits_left = 6
#
#struct.read(5)
#bits_left = 1
#
#struct.read(5)
#super.read(1)
#bits_left = 4


class Structure(bin.Structure, metaclass=BitStructureMetaclass):
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
            bytes, value = field.read_value(self)
            bit_buffer = (bit_buffer << size) | value
        self.bits_left = 8 % size
        bits = bit_buffer >> self.bits_left
        self._bit_buffer = bit_buffer & (1 << self._bits_left) - 1
        return bits


class Integer(bin.Integer):
    def __init__(self, *args, **kwargs):
        super(Flag, self).__init__(*args, size=int((size + 7) / 8), **kwargs)
        self.size = size

    def encode(self, value):
        if value > (1 << self.size) - 1:
            raise ValueError("Value is large for this field.")
        return super(Integer, self).encode(value) & ((1 << self.size) - 1)


class Flag(Integer):
    size = args.Override(default=1)

    def encode(self, value):
        return int(super(Flag, self).encode(value))

    def decode(self, value):
        return bool(super(Flag, self).decode(value))


