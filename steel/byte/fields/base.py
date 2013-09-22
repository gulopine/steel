import sys

from steel.common import args, fields

__all__ = ['Field', 'Reserved']


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


class Reserved(Field):
    default = args.Override(default=None)

    def __init__(self, *args, **kwargs):
        super(Reserved, self).__init__(*args, **kwargs)

        # Hack to add the reserved field to the class without
        # having to explicitly give it a (likely useless) name
        frame = sys._getframe(2)
        locals = frame.f_locals
        locals[self.get_available_name(locals.keys())] = self

    def get_available_name(self, locals):
        i = 0
        while True:
            name = '_reserved_%s' % i
            if name not in locals:
                return name
            i += 1

    def set_name(self, name):
        if hasattr(self, 'name'):
            raise TypeError('Reserved fields must not be given an attribute name')
        super(Reserved, self).set_name(name)

    def encode(self, value):
        return b'\x00' * self.size

    def decode(self, value):
        return None


