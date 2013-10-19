import io

from steel.common import args, fields, Remainder

__all__ = ['List', 'Object']


class List(fields.Field):
    size = args.Override(default=None)

    def __init__(self, field, *args, **kwargs):
        super(List, self).__init__(*args, **kwargs)
        self.field = field

    def read(self, file):
        value_bytes = b''
        values = []
        with self.for_instance(self.instance):
            if self.size == -1:
                while True:
                    bytes, value = self.field.read_value(file)
                    if bytes:
                        values.append(value)
                        value_bytes += bytes
                    else:
                        break
            for i in range(self.size):
                bytes, value = self.field.read_value(file)
                value_bytes += bytes
                values.append(value)
        raise fields.FullyDecoded(value_bytes, values)

    def encode(self, values):
        encoded_values = []
        with self.for_instance(self.instance):
            for value in values:
                encoded_values.append(self.field.encode(value))
        return b''.join(encoded_values)


class Object(fields.Field):
    size = args.Override(default=None)

    def __init__(self, structure, *args, **kwargs):
        self.structure = structure
        super(Object, self).__init__(*args, **kwargs)

    def read(self, file):
        value = self.structure(file)
        value._parent = file

        # Force the evaluation of the entire structure in
        # order to make sure other fields work properly
        value_bytes = value.get_raw_bytes()

        raise fields.FullyDecoded(value_bytes, value)

    def encode(self, value):
        output = io.BytesIO()
        value.save(output)
        return output.getvalue()

    def __getattr__(self, name):
        if 'structure' in self.__dict__:
            field = getattr(self.structure, name)
            if field in self.structure._fields.values():
                field = copy.copy(field)
                field._parent = self
                return field
        raise AttributeError(name)
