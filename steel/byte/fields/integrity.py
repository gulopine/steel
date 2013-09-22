import collections
import functools
import zlib

from steel.fields.numbers import Integer
from steel.common import args, fields

__all__ = ['CheckSum', 'CRC32', 'Adler32', 'IntegrityError']


class IntegrityError(ValueError):
    pass


class CheckSum(Integer):
    first = args.Argument(default=None)
    last = args.Argument(default=None)

    def attach_to_class(self, cls):
        super(CheckSum, self).attach_to_class(cls)

        self.fields = []
        in_range = False
        for field in cls._fields.values():
            if field is self:
                # Can't go beyond the integrity field itself
                break

            if self.first is None:
                self.first = field

            if field is self.first:
                in_range = True

            if in_range:
                self.fields.append(field)
                field.after_encode(self.update_encoded_value)

            if field is self.last:
                # End of the line
                break

    def build_cache(self, instance):
        for field in self.fields:
            if field.name not in instance._raw_values:
                # Set the value to itself just to update the encoded value
                setattr(instance, field.name, getattr(instance, field.name))

    def read(self, file):
        try:
            given_bytes = super(CheckSum, self).read(file)
            given_value = super(CheckSum, self).decode(given_bytes)
        except fields.FullyDecoded as obj:
            given_bytes = obj.bytes
            given_value = obj.value
        self.build_cache(file)
        if given_value != self.get_calculated_value(file):
            raise IntegrityError('%s does not match calculated value' % self.name)
        raise fields.FullyDecoded(given_bytes, given_value)

    def get_calculated_value(self, instance):
        data = b''.join(instance._extract(field) for field in self.fields)
        return self.calculate(data) & ((1 << self.size * 8) - 1)

    def update_encoded_value(self, instance, value):
        setattr(instance, self.name, self.get_calculated_value(instance))

    def calculate(self, data):
        return sum(data)


class CRC32(CheckSum):
    size = args.Override(default=4)

    def calculate(self, data):
        return zlib.crc32(data)


class Adler32(CheckSum):
    size = args.Override(default=4)

    def calculate(self, data):
        return zlib.adler32(data)


