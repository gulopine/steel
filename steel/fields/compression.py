import io
import zlib

from steel.fields import Field
from steel import common


class Zlib(Field):
    def __init__(self, field, *args, **kwargs):
        super(Zlib, self).__init__(*args, **kwargs)
        self.field = field

    def decode(self, value):
        data = zlib.decompress(value)
        with self.for_instance(self.instance):
            return self.field.decode(data)

    def encode(self, value):
        data = self.field.encode(value)
        return zlib.compress(data)

