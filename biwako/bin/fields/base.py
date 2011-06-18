import copy
import functools

from ...common import args, meta
from ..conditional import Condition

class Trigger:
    def __init__(self):
        self.cache = {}
        self.functions = set()

    def __call__(self, func):
        # Used as a decorator
        self.functions.add(func)

    def __get__(self, instance, owner):
        if owner is None:
            return self
        if instance not in self.cache:
            self.cache[instance] = BoundTrigger(instance, self.functions)
        return self.cache[instance]


class BoundTrigger:
    def __init__(self, field, functions):
        self.field = field
        self.functions = set(functools.partial(func, field) for func in functions)

    def __iter__(self):
        return iter(self.functions)

    def __call__(self, func):
        # Used as a decorator
        self.functions.add(func)

    def apply(self, *args, **kwargs):
        # Called from within the appropriate code
        for func in self.functions:
            func(*args, **kwargs)


class Field(metaclass=meta.DeclarativeFieldMetaclass):
    size = args.Argument(resolve_field=True)
    offset = args.Argument(default=None, resolve_field=True)
    choices = args.Argument(default=())
    default = args.Argument(default=args.NotProvided)

    after_encode = Trigger()
    after_decode = Trigger()

    @after_encode
    def update_size(self, obj, value):
        if isinstance(self.size, Field):
            setattr(obj, self.size.name, len(value))

    def __init__(self, label='', **kwargs):
        self.label = label
        self._parent = None
        self.instance = None

        for name, arg in self.arguments.items():
            if name in kwargs:
                value = kwargs.pop(name)
            elif arg.has_default:
                value = arg.default
            else:
                raise TypeError("The %s argument is required for %s fields" % (arg.name, self.__class__.__name__))
            setattr(self, name, value)
        if kwargs:
            raise TypeError("%s is not a valid argument for %s fields" % (list(kwargs.keys())[0], self.__class__.__name__))

        # Once the base values are all in place, arguments can be initialized properly
        for name, arg in self.arguments.items():
            if hasattr(self, name):
                value = getattr(self, name)
            else:
                value = None
            setattr(self, name, arg.initialize(self, value))

    def resolve(self, instance):
        if self._parent is not None:
            instance = self._parent.resolve(instance)
        return getattr(instance, self.name)

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

    def set_name(self, name):
        self.name = name
        label = self.label or name.replace('_', ' ')
        self.label = label.title()

    def attach_to_class(self, cls):
        cls._fields.append(self)

    def validate(self, obj, value):
        # This should raise a ValueError if the value is invalid
        # It should simply return without an error if it's valid
        with self.for_instance(obj):
            # First, make sure the value can be encoded
            self.encode(value)
    
            # Then make sure it's a valid option, if applicable
            if self.choices and value not in set(v for v, desc in self.choices):
                raise ValueError("%r is not a valid choice" % value)

    def _extract(self, instance):
        with self.for_instance(instance):
            try:
                return self.read(instance), None
            except FullyDecoded as obj:
                return obj.bytes, obj.value

    def read_value(self, file):
        try:
            bytes = self.read(file)
            value = self.decode(bytes)
            return bytes, value
        except FullyDecoded as obj:
            return obj.bytes, obj.value

    def for_instance(self, instance):
        return meta.AttributeInstance(self, instance)

    def __get__(self, instance, owner):
        if not instance:
            return self

        # Customizes the field for this particular instance
        # Use field instead of self for the rest of the method
        with self.for_instance(instance):
            try:
                value = instance._extract(self)
            except IOError:
                if self.default is not args.NotProvided:
                    return self.default
                raise AttributeError("Attribute %r has no data" % self.name)
    
            if self.name not in instance.__dict__:
                instance.__dict__[self.name] = self.decode(value)
                self.after_decode.apply(instance, value)
            return instance.__dict__[self.name]

    def __set__(self, instance, value):
        with self.for_instance(instance):
            instance.__dict__[self.name] = value
            instance._raw_values[self.name] = self.encode(value)
        self.after_encode.apply(instance, value)

    def __repr__(self):
        return '<%s: %s>' % (self.name, type(self).__name__)

    def __hash__(self):
        return id(self)

    def __eq__(self, other):
        return Condition(self, other, lambda a, b: a == b)

    def __ne__(self, other):
        return Condition(self, other, lambda a, b: a != b)


class FullyDecoded(Exception):
    def __init__(self, bytes, value):
        self.bytes = bytes
        self.value = value


