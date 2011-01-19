# Special object used to instruct the reader to continue to the end of the file
Remainder = object()


class FieldMeta(type):
    def __call__(cls, *args, **kwargs):
        field = super(FieldMeta, cls).__call__(*args, **kwargs)
        field._arguments = (args, kwargs)
        return field


class Field(metaclass=FieldMeta):
    def __init__(self, label=None, size=None, offset=None, **kwargs):
        self.label = label
        self.size = size
        self.offset = offset

    def calculate_size(self, obj):
        return self.size

    def read(self, obj):
        size = self.calculate_size(obj)

        # In this special case, the field gets everything that's left
        if self.size is Remainder:
            return obj.read()

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

    def attach_to_class(self, cls, name, **options):
        # Supply any inherited arguments to the constructor
        args, kwargs = self._arguments
        options.update(kwargs)
        self.__init__(*args, **options)

        self.name = name
        label = self.label or name.replace('_', ' ')
        self.label = label.title()
        cls._fields.append(self)

    def __get__(self, instance, owner):
        if not instance:
            return self
        if self.name not in instance.__dict__:
            instance.__dict__[self.name] = instance._get_value(self)
        return instance.__dict__[self.name]

