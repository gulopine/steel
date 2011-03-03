import io

from .base import Field, FullyDecoded
from ..fields import args


class SubStructure(Field):
    size = args.Override(default=None)

    def __init__(self, structure, *args, **kwargs):
        self.structure = structure
        super(SubStructure, self).__init__(*args, **kwargs)

    def read(self, file):
        value = self.structure(file)

        value_bytes = b''
        # Force the evaluation of the entire structure in
        # order to make sure other fields work properly
        for field in self.structure._fields:
            getattr(value, field.name)
            value_bytes += value._raw_values[field.name]

        raise FullyDecoded(value_bytes, value)

    def encode(self, value):
        output = io.BytesIO()
        value.save(output)
        return output.getvalue()


class List(Field):
    size = args.Override(default=None)

    def __init__(self, field, *args, **kwargs):
        super(List, self).__init__(*args, **kwargs)
        self.field = field

    def read(self, file):
        value_bytes = b''
        values = []
        instance_field = self.field.for_instance(self.instance)

        for i in range(self.size):
            bytes, value = instance_field.read_value(file)
            value_bytes += bytes
            values.append(value)
        raise FullyDecoded(value_bytes, values)

    def encode(self, values):
        encoded_values = []
        if self.instance:
            instance_field = self.field.for_instance(self.instance)
        else:
            instance_field = self.field
        for value in values:
            encoded_values.append(instance_field.encode(value))
        return b''.join(encoded_values)


