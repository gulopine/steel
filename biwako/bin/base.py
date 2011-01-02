class StructureMeta(type):
    def __init__(self, name, bases, attrs):
        print('blah')

class Structure(metaclass=StructureMeta):
    pass
