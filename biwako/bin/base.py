class StructureMeta(type):
    def __init__(self, name, bases, attrs):
        pass

class Structure(metaclass=StructureMeta):
    pass
