import copy
import io

from .base import Field, FullyDecoded
from biwako import args


class SubStructure(Field):
    size = args.Override(default=None)

    def __init__(self, structure, *args, **kwargs):
        self.structure = structure
        super(SubStructure, self).__init__(*args, **kwargs)

    def read(self, file):
        value = self.structure(file)

        if type(value) in Parent.assigned_names:
            name = Parent.assigned_names[type(value)]
            print('Assigning parent (%r) to value (%r) as %s!' % (file, value, name))
            setattr(value, name, file)

        # Force the evaluation of the entire structure in
        # order to make sure other fields work properly
        value_bytes = value.get_raw_bytes()

        raise FullyDecoded(value_bytes, value)

    def encode(self, value):
        output = io.BytesIO()
        value.save(output)
        return output.getvalue()

    def __getattr__(self, name):
        if 'structure' in self.__dict__:
            field = getattr(self.structure, name)
            if field in self.structure._fields:
                field = copy.copy(field)
                field._parent = self
                return field
        raise AttributeError(name)


class List(Field):
    size = args.Override(default=None)

    def __init__(self, field, *args, **kwargs):
        super(List, self).__init__(*args, **kwargs)
        self.field = field

    def read(self, file):
        value_bytes = b''
        values = []
        instance_field = self.field.for_instance(self.instance)

        for i in range(self.size):
            bytes, value = instance_field.read_value(file)
            value_bytes += bytes
            values.append(value)
        raise FullyDecoded(value_bytes, values)

    def encode(self, values):
        encoded_values = []
        if self.instance:
            instance_field = self.field.for_instance(self.instance)
        else:
            instance_field = self.field
        for value in values:
            encoded_values.append(instance_field.encode(value))
        return b''.join(encoded_values)


class Parent(Field):
    assigned_names = {}
    size = args.Override(default=None)

    def __init__(self, parent=None, attr=None):
        self._parent = parent
        self.attr = attr
        super(Parent, self).__init__()

    def __getattr__(self, name):
        # Don't interfere with private attributes or Python's magic methods
        if not name.startswith('_'):
            print('Getting attribute %r' % name)
            return Parent(self, name)
        raise AttributeError(name)

    def resolve(self, instance):
        print('Resolving parent')
        print('Resolving parent: %s' % self.name)
        print('For instance %r' % instance)
        if self._parent is not None:
            instance = self._parent.resolve(instance)
        return getattr(instance, self.name)

    def set_name(self, name):
        print('Setting name to %r' % name)
        self.name = name

    def attach_to_class(self, cls):
        self.assigned_names[cls] = self.name

    def read(self, size=None):
        return b''

    def encode(self, value):
        return value

    def decode(self, value):
        return value


