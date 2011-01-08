import collections

class StructureMeta(type):
    def __init__(cls, name, bases, attrs):
        cls._fields = []
        for name, attr in attrs.items():
            if hasattr(attr, 'attach_to_class'):
                attr.attach_to_class(cls, name)

    @classmethod
    def __prepare__(metacls, name, bases, **kwargs):
        return collections.OrderedDict()

    def __iter__(cls):
        return iter(cls.__dict__)

class Structure(metaclass=StructureMeta):
    pass
