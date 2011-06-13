import copy
import io

from .base import Field, FullyDecoded
from biwako import args
from biwako import common


class SubStructure(Field):
    size = args.Override(default=None)

    def __init__(self, structure, *args, **kwargs):
        self.structure = structure
        super(SubStructure, self).__init__(*args, **kwargs)

    def read(self, file):
        value = self.structure(file)

        # Force the evaluation of the entire structure in
        # order to make sure other fields work properly
        value_bytes = value.get_raw_bytes()

        raise FullyDecoded(value_bytes, value)

    def encode(self, value):
        output = io.BytesIO()
        value.save(output)
        return output.getvalue()

    def __getattr__(self, name):
        if 'structure' in self.__dict__:
            field = getattr(self.structure, name)
            if field in self.structure._fields:
                field = copy.copy(field)
                field._parent = self
                return field
        raise AttributeError(name)


class List(Field):
    size = args.Override(default=None)

    def __init__(self, field, *args, **kwargs):
        super(List, self).__init__(*args, **kwargs)
        self.field = field

    def read(self, file):
        value_bytes = b''
        values = []
        with common.AttributeInstance(self.instance):
            for i in range(self.size):
                bytes, value = self.field.read_value(file)
                value_bytes += bytes
                values.append(value)
        raise FullyDecoded(value_bytes, values)

    def encode(self, values):
        encoded_values = []
        with common.AttributeInstance(self.instance):
            for value in values:
                encoded_values.append(self.field.encode(value))
        return b''.join(encoded_values)


