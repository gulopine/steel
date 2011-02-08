import io
import zlib

from .base import Field


class Zlib(Field):
    def __init__(self, field, *args, **kwargs):
        super(Zlib, self).__init__(*args, **kwargs)
        self.field = field

    def extract(self, obj):
        data = obj.read(self.size(obj))
        data = zlib.decompress(data)
        return self.field.extract(io.BytesIO(data))

    def encode(self, obj, value):
        data = self.field.encode(obj, value)
        return zlib.compress(data)

