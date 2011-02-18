import collections
import functools

from .numbers import Integer


class CheckSum(Integer):
    def __init__(self, *args, first=None, last=None, **kwargs):
        super(CheckSum, self).__init__(*args, **kwargs)
        self.first = first
        self.last = last

    def attach_to_class(self, cls):
        super(CheckSum, self).attach_to_class(cls)

        self.fields = []
        in_range = False
        for field in cls._fields:
            if field is self:
                # Can't go beyond the integrity field itself
                break

            if self.first is None:
                self.first = field

            if field is self.first:
                in_range = True

            if in_range:
                self.fields.append(field)
                func = functools.partial(self.update_cache, field.name)
                field.after_encode(self.update_encoded_value)
#                field.after_encode(func)

            if field is self.last:
                # End of the line
                break

    def update_cache(self, name, instance, value):
        if self.name not in instance.__dict__:
            # Set up a cache for storing encoded values
            fields = ((field.name, b'') for field in self.fields)
            instance.__dict__[self.name] = collections.OrderedDict(fields)
        instance.__dict__[self.name][name] = value

    def update_encoded_value(self, instance, value):
        data = b''
        for field in self.fields:
            if field.get_encoded_name() not in instance.__dict__:
                # Set the value to itself just to update the encoded value
                setattr(instance, field.name, getattr(instance, field.name))
            data += instance.__dict__[field.get_encoded_name()]
        setattr(instance, self.name, self.calculate(data))

    def calculate(self, data):
        return sum(data)


