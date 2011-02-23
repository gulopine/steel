import io
import zlib

from .base import Field


class Zlib(Field):
    def __init__(self, field, *args, **kwargs):
        super(Zlib, self).__init__(*args, **kwargs)
        self.field = field

    def extract(self, obj):
        data = obj.read(self.size)
        data = zlib.decompress(data)
        return self.field.extract(io.BytesIO(data))

    def encode(self, value):
        data = self.field.encode(value)
        return zlib.compress(data)

