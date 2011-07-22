from ..common import args
from ..byte import fields
from ..common.fields import *
from ..byte.fields import numbers

__all__ = ['Field', 'Integer', 'FixedInteger', 'Flag', 'Reserved']


class Field(fields.Field):
    size = args.Argument(resolve_field=True)
    choices = args.Argument(default=())
    default = args.Argument(default=args.NotProvided)

    def __init__(self, label='', **kwargs):
        self.label = label

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
            setattr(self, name, arg.initialize(self, getattr(self, name)))


class Integer(numbers.Integer):
    size = args.Override(resolve_field=False)
    signed = args.Argument(default=False)

    def encode(self, value):
        if value > (1 << self.size) - 1:
            raise ValueError("Value is too large for this field.")
        return value & ((1 << self.size) - 1)

    def decode(self, value):
        if value > (1 << self.size) - 1:
            raise ValueError("Value is too large for this field.")
        return value & ((1 << self.size) - 1)


class FixedInteger(Integer):
    def __init__(self, value, *args, **kwargs):
        super(FixedInteger, self).__init__(*args, signed=value < 0, **kwargs)
        self.decoded_value = value
        self.encoded_value = super(FixedInteger, self).encode(value)

    def encode(self, value):
        if value != self.decoded_value:
            raise ValueError('Expected %r, got %r.' % (self.decoded_value, value))
        return self.encoded_value

    def decode(self, value):
        if value != self.encoded_value:
            raise ValueError('Expected %r, got %r.' % (self.encoded_value, value))
        return self.decoded_value


class Flag(Integer):
    size = args.Override(default=1)

    def encode(self, value):
        return int(super(Flag, self).encode(value))

    def decode(self, value):
        return bool(super(Flag, self).decode(value))


class Reserved(fields.Reserved):
    def encode(self, value):
        return 0


