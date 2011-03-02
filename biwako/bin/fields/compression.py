import io
import zlib

from .base import Field


class Zlib(Field):
    def __init__(self, field, *args, **kwargs):
        super(Zlib, self).__init__(*args, **kwargs)
        self.field = field

    def extract(self, instance):
        field = self.for_instance(instance)
        data = zlib.decompress(instance.read(field.size))
        other_field = self.field.for_instance(instance)
        return other_field.extract(io.BytesIO(data))

    def encode(self, value):
        data = self.field.encode(value)
        return zlib.compress(data)

