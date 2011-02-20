import collections
import functools
import zlib

from .numbers import Integer


class IntegrityError(ValueError):
    pass


class CheckSum(Integer):
    def __init__(self, *args, first=None, last=None, **kwargs):
        super(CheckSum, self).__init__(*args, **kwargs)
        self.first = first
        self.last = last

    def attach_to_class(self, cls):
        super(CheckSum, self).attach_to_class(cls)

        self.fields = []
        in_range = False
        for field in cls._fields:
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
            if field.get_encoded_name() not in instance.__dict__:
                # Set the value to itself just to update the encoded value
                setattr(instance, field.name, getattr(instance, field.name))

    def extract(self, obj):
        given_value = super(CheckSum, self).extract(obj)
        self.build_cache(obj)
        if given_value != self.get_calculated_value(obj):
            raise IntegrityError('%s does not match calculated value' % self.name)
        return given_value

    def get_calculated_value(self, instance):
        data = b''.join(instance.__dict__[field.get_encoded_name()] for field in self.fields)
        return self.calculate(data)

    def update_encoded_value(self, instance, value):
        self.build_cache(instance)
        setattr(instance, self.name, self.get_calculated_value(instance))

    def calculate(self, data):
        return sum(data)


class CRC32(CheckSum):
    def __init__(self, *args, **kwargs):
        super(CRC32, self).__init__(*args, size=4, **kwargs)

    def calculate(self, data):
        return zlib.crc32(data) & 0xffffffff


class Adler32(CheckSum):
    def __init__(self, *args, **kwargs):
        super(Adler32, self).__init__(*args, size=4, **kwargs)

    def calculate(self, data):
        return zlib.adler32(data) & 0xffffffff


