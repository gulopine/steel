from .base import Field


class Reserved(Field):
    def encode(self, obj, value):
        return b'\x00' * self.size(obj)

    def decode(self, value):
        return None


