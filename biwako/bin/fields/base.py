import collections

# Special object used to instruct the reader to continue to the end of the file
Remainder = object()


class FieldMeta(type):
    def __init__(cls, name, bases, attrs):
        for name, attr in attrs.items():
            if hasattr(attr, 'attach_to_class'):
                attr.attach_to_class(cls, name)

    @classmethod
    def __prepare__(metacls, name, bases):
        return collections.OrderedDict()


class Field(metaclass=FieldMeta):
    def __init__(self, label=None, size=None, offset=None, **kwargs):
        self.label = label
        self.size = size
        self.offset = offset
        for name, value in kwargs.items():
            if hasattr(self, name):
                attr = getattr(self.__class__, name)
                if isinstance(attr, Option):
                    value = attr.initialize(self, value)
                    self.__dict__[name] = value

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
        self.name = name
        label = self.label or name.replace('_', ' ')
        self.label = label.title()
        cls._fields.append(self)

        for name, value in options.items():
            if name not in self.__dict__ and hasattr(self, name):
                attr = getattr(self.__class__, name)
                if isinstance(attr, Option):
                    value = attr.initialize(self, value)
                    self.__dict__[name] = value
                setattr(cls, name, value)

    def __get__(self, instance, owner):
        if not instance:
            return self
        if self.name not in instance.__dict__:
            instance.__dict__[self.name] = instance._get_value(self)
        return instance.__dict__[self.name]


class Option:
    def __init__(self, default=None):
        self.default = default
        self.initialize = lambda obj, value: value

    def attach_to_class(self, cls, name):
        self.name = name

    def init(self, func):
        # Decorator to define an initialization method
        self.initialize = func

    def __get__(self, instance, owner):
        if not instance:
            return self

        if self.name not in instance.__dict__:
            value = self.initialize(instance, self.default)
            instance.__dict__[self.name] = value
        return instance.__dict__[self.name]

    def __set__(self, instance, value):
        instance.__dict__[self.name] = value

