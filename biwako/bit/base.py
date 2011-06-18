import sys

from ..common import args
from biwako import bin

__all__ = ['Structure']


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


