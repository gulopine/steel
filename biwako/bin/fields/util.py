from .base import Field


class List(Field):
    def __init__(self, field, *args, **kwargs):
        super(List, self).__init__(*args, **kwargs)
        self.field = field

    def calculate_size(self, obj):
        field_size = self.field.calculate_size(obj)
        return field_size * super(List, self).calculate_size(obj)

    def extract(self, obj):
        values = []
        for i in range(self.size(obj)):
            values.append(self.field.extract(obj))
        return values

    def encode(self, obj, values):
        encoded_values = []
        for value in values:
            encoded_values.append(self.field.encode(obj, value))
        return b''.join(encoded_values)

class Reserved(Field):
    def encode(self, obj, value):
        return b'\x00' * self.size

    def decode(self, value):
        return None


