from steel.common import args, fields

__all__ = ['List']


class List(fields.Field):
    size = args.Override(default=None)

    def __init__(self, field, *args, **kwargs):
        super(List, self).__init__(*args, **kwargs)
        self.field = field

    def read(self, file):
        value_bytes = b''
        values = []
        with self.for_instance(self.instance):
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
