from .base import Field


class String(Field):
    def __init__(self, *args, encoding='utf8', **kwargs):
        super(String, self).__init__(*args, **kwargs)
        ''.encode(encoding)
        self.encoding = encoding

    def encode(self, value):
        return value.encode(self.encoding)

    def decode(self, value):
        return value.decode(self.encoding)


class String(Field):
    pass


