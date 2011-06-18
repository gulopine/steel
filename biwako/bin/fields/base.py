from ...common import args, fields

__all__ = ['Field']


class Field(fields.Field):
    offset = args.Argument(default=None, resolve_field=True)

    @fields.Field.after_encode
    def update_size(self, obj, value):
        if isinstance(self.size, Field):
            setattr(obj, self.size.name, len(value))

    def read(self, obj):
        # If the size can be determined easily, read
        # that number of bytes and return it directly.
        if self.size is not None:
            return obj.read(self.size)

        # Otherwise, the field needs to supply its own
        # technique for determining how much data to read.
        raise NotImplementedError()

    def write(self, obj, value):
        # By default, this doesn't do much, but individual
        # fields can/should override it if necessary
        obj.write(value)


