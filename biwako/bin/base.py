import collections

class StructureMeta(type):
    def __new__(cls, name, bases, attrs, **options):
        # Nothing to do here, but we need to make sure options
        # don't get passed in to type.__new__() itself.
        return type.__new__(cls, name, bases, attrs)

    def __init__(cls, name, bases, attrs, **options):
        cls._fields = []
        for name, attr in attrs.items():
            if hasattr(attr, 'attach_to_class'):
                attr.attach_to_class(cls, name, **options)

    @classmethod
    def __prepare__(metacls, name, bases, **options):
        return collections.OrderedDict()

    def __iter__(cls):
        return iter(cls.__dict__)

class Structure(metaclass=StructureMeta):
    def __init__(self, *args, **kwargs):
        self.file = len(args) > 0 and args[0] or None
        self.mode = self.file and 'rb' or 'wb'
        self.position = 0

        if self.file and kwargs:
            raise TypeError("Cannot supply a file and attributes together")

        for name, value in kwargs.items():
            setattr(self, name, value)

    def read(self, size=None):
        if self.mode != 'rb':
            raise IOError("not readable")
        return self.file.read(size)

    def write(self, data):
        if self.mode != 'wb':
            raise IOError("not writable")
        pass


