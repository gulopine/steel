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
    def __init__(self, *args, **kwargs):
        self.file = len(args) > 0 and args[0] or None
        self.mode = self.file and 'rb' or 'wb'
        self.position = 0

    def read(self, size=None):
        if self.mode != 'rb':
            raise IOError("not readable")
        return self.file.read(size)

    def write(self, data):
        if self.mode != 'wb':
            raise IOError("not writable")
        pass


