import functools

from biwako import common, args


class Field(metaclass=common.DeclarativeFieldMetaclass):
    """
    An individual column within a CSV file. This serves as a base for attributes
    and methods that are common to all types of fields. Subclasses of Field
    will define behavior for more specific data types.
    """
    required = args.Argument(default=True)
    choices = args.Argument(default=())

    def __init__(self, label=None, **kwargs):
        self.name = ''
        self.label = label
        self._validators = [self.decode]

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

    def set_name(self, name):
        self.name = name
        label = self.label or name.replace('_', ' ')
        self.label = label.title()

    def attach_to_class(self, cls):
        cls._fields.append(self)

    def encode(self, value):
        """
        Convert the given Python object to a string.
        """
        return str(value)

    def decode(self, value):
        """
        Convert the given string to a native Python object.
        """
        return value

    def validator(self, func):
        self._validators.append(functools.partial(func, self))
        return func

    def validate(self, value):
        """
        Validate that the given value matches the field's requirements.
        Raise a ValueError only if the given value was invalid.
        """
        for validate in self._validators:
            validate(value)


