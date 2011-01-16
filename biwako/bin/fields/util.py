from .base import Field


class List(Field):
    def __init__(self, field, *args, **kwargs):
        super(List, self).__init__(*args, **kwargs)
        self.field = field

    def calculate_size(self, obj):
        field_size = self.field.calculate_size(obj)
        return field_size * super(List, self).calculate_size(obj)

    def read(self, obj):
        values = []
        for i in range(super(List, self).calculate_size(obj)):
            values.append(self.field.read(obj))
        return values

    def encode(self, values):
        encoded_values = []
        for value in values:
            encoded_values.append(self.field.encode(value))
        return b''.join(encoded_values)

    def decode(self, values):
        decoded_values = []
        for value in values:
            decoded_values.append(self.field.decode(value))
        return decoded_values

