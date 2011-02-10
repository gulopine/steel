from ...bin import data


class Trigger:
    def __init__(self):
        self.functions = set()

    def __iter__(self):
        return iter(self.function)

    def __call__(self, func):
        # Used as a decorator
        self.functions.add(func)

    def apply(self, *args, **kwargs):
        # Called from within the appropriate code
        for func in self.functions:
            func(*args, **kwargs)


class FieldMeta(type):
    def __call__(cls, *args, **kwargs):
        if data.fields.options:
            options = data.fields.options.copy()
            options.update(kwargs)
        else:
            options = kwargs
        return super(FieldMeta, cls).__call__(*args, **options)


class Field(metaclass=FieldMeta):
    def __init__(self, label=None, *, size=None, offset=None, choices=(), **kwargs):
        self.label = label
        self.size = DynamicValue(size)
        self.offset = offset
        # TODO: Actually support choices properly later
        self.choices = choices

    def extract(self, obj):
        return self.decode(self.read(obj))

    def read(self, obj):
        size = self.size(obj)

        # If the size can be determined easily, read
        # that number of bytes and return it directly.
        if size is not None:
            return obj.read(size)

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

    def validate(self, obj, value):
        # This should raise a ValueError if the value is invalid
        # It should simply return without an error if it's valid

        # First, make sure the value can be encoded
        self.encode(obj, value)

        # Then make sure it's a valid option, if applicable
        if self.choices and value not in set(v for v, desc in self.choices):
            raise ValueError("%r is not a valid choice" % value)

    def get_encoded_name(self):
        return '%s_encoded' % self.name

    after_encode = Trigger()
    after_extract = Trigger()

    def __get__(self, instance, owner):
        if not instance:
            return self
        if self.name not in instance.__dict__:
            try:
                instance.__dict__[self.name] = instance._get_value(self)
                self.after_extract.apply(instance, instance.__dict__[self.name])
            except IOError:
                raise AttributeError("Attribute %r has no data" % self.name)
        return instance.__dict__[self.name]

    def __set__(self, instance, value):
        instance.__dict__[self.name] = value
        instance.__dict__[self.get_encoded_name()] = self.encode(instance, value)
        self.after_encode.apply(instance, value)

    def __repr__(self):
        return '<%s: %s>' % (self.name, type(self).__name__)


class DynamicValue:
    def __init__(self, value):
        self.value = value

    def __call__(self, obj):
        if isinstance(self.value, DynamicValue):
            return self.value(obj)
        elif isinstance(self.value, Field):
            return obj._get_value(self.value)
        elif hasattr(self.value, '__call__'):
            return self.value(obj)
        else:
            return self.value


# Special object used to instruct the reader to continue to the end of the file
def Remainder(obj):
    return -1


