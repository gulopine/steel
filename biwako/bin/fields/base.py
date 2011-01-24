import threading

# Special object used to instruct the reader to continue to the end of the file
Remainder = object()


class FieldMeta(type):
    _registry = threading.local()
    _registry.options = {}

    def __call__(cls, *args, **kwargs):
        if FieldMeta._registry.options:
            options = FieldMeta._registry.options.copy()
            options.update(kwargs)
        else:
            options = kwargs
        return super(FieldMeta, cls).__call__(*args, **options)


class Field(metaclass=FieldMeta):
    def __init__(self, label=None, size=None, offset=None, choices=(), **kwargs):
        self.label = label
        self.size = size
        self.offset = offset
        # TODO: Actually support choices properly later
        self.choices = choices

    def calculate_size(self, obj):
        if isinstance(self.size, Field):
            size = obj._get_value(self.size)
            return size
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

    def set_name(self, name):
        self.name = name
        label = self.label or name.replace('_', ' ')
        self.label = label.title()

    def attach_to_class(self, cls):
        cls._fields.append(self)

    def __get__(self, instance, owner):
        if not instance:
            return self
        if self.name not in instance.__dict__:
            try:
                instance.__dict__[self.name] = instance._get_value(self)
            except IOError:
                raise AttributeError("Attribute %r has no data" % self.name)
        return instance.__dict__[self.name]

    def __set__(self, instance, value):
        instance.__dict__[self.name] = value

