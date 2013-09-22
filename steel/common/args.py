import copy

from steel.common import data

NotProvided = object()

class Argument:
    def __init__(self, positional=False, resolve_field=False, **kwargs):
        self.resolve_field = resolve_field

        # Default can be None, so we have to do some extra work to
        # fall back in the event that no defualt value was provided
        if 'default' in kwargs:
            self.default = kwargs.pop('default')
        else:
            self.default = None
            self.has_default = False

        # Because of all that default mess, we need to make sure kwargs
        # doesn't have any arguments we don't know how to deal with
        if kwargs:
            # Just grab the first one to show in the error message
            raise TypeError('Unknown argument %r' % iter(kwargs).__next__())

    @property
    def default(self):
        return self.__dict__['default']

    @default.setter
    def default(self, value):
        self.__dict__['default'] = value
        self.has_default = True

    @default.deleter
    def default(self):
        self.__dict__['default'] = None
        self.has_default = False

    def set_name(self, name):
        self.name = name

    def attach_to_class(self, cls):
        cls.arguments[self.name] = self

    def init(self, func):
        # Decorator for setting an initialization function
        self.initialize = func
        return func

    def initialize(self, instance, value):
        # By default, initialization doesn't do anything
        return value

    def __get__(self, instance, owner):
        arg = instance.arguments[self.name]
        try:
            value = instance.__dict__[arg.name]
        except KeyError:
            raise AttributeError(self.name)
        key = hash(instance)
        if data.instance_stack[key]:
            instance = data.instance_stack[key][-1]
            if arg.resolve_field and hasattr(value, 'resolve'):
                value = value.resolve(instance)
            elif hasattr(value, '__call__'):
                value = value(instance)
        return value

    def __set__(self, instance, value):
        instance.__dict__[self.name] = value


class Override(Argument):
    def __init__(self, **kwargs):
        # For now, just save the arguments for later
        self.overrides = kwargs.copy()

        # Default can be None, so we have to do some extra work to
        # fall back in the event that no defualt value was provided
        if 'default' in kwargs:
            self.default = kwargs.pop('default')
        else:
            self.default = None
            self.has_default = False

    def attach_to_class(self, cls):
        if self.name not in cls.arguments:
            raise TypeError("%r is not an argument, so it can't be overridden" % self.name)

        argument = copy.copy(cls.arguments[self.name])
        # Replace the original options with any replacements provided
        for name, value in self.overrides.items():
            if hasattr(argument, name):
                setattr(argument, name, value)
            else:
                raise TypeError("%r is not an attribute of %r, so it can't be overridden" % (name, self.name))

        cls.arguments[self.name] = argument

class Removed(Argument):
    def __init__(self):
        # Nothing to do for this part of the process, we just
        # need to prevent the normal behavior from taking place
        pass

    def attach_to_class(self, cls):
        # Remove the argument from the class
        try:
            del cls.arguments[self.name]
        except KeyError:
            raise TypeError("%r is not an argument, so it can't be removed" % self.name)


