import functools

from ...bin import data


class FieldMeta(type):
    def __call__(cls, *args, **kwargs):
        if data.field_options:
            options = data.field_options.copy()
            options.update(kwargs)
        else:
            options = kwargs
        return super(FieldMeta, cls).__call__(*args, **options)


class Field(metaclass=FieldMeta):
    """
    An individual column within a CSV file. This serves as a base for attributes
    and methods that are common to all types of fields. Subclasses of Field
    will define behavior for more specific data types.
    """

    def __init__(self, label=None, *, required=True, choices=()):
        self.name = ''
        self.label = label
        self.required = required
        self._validators = [self.decode]
        self.choices = choices

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


