import io
from .base import Field, DynamicValue


class SubStructure(Field):
    def __init__(self, structure, *args, **kwargs):
        self.structure = structure
        super(SubStructure, self).__init__(*args, **kwargs)

    def extract(self, obj):
        value = self.structure(obj)
        
        # Force the evaluation of the entire structure in
        # order to make sure other fields work properly
        for field in self.structure._fields:
            getattr(value, field.name)

        return value

    def encode(self, obj, value):
        output = io.BytesIO()
        value.save(output)
        return output.getvalue()


class List(Field):
    def __init__(self, field, *args, **kwargs):
        super(List, self).__init__(*args, **kwargs)
        self.field = field

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


