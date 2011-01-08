class Field:
    def __init__(self, label=None, size=None):
        self.label = label
        self.size = size

    def calculate_size(self, obj):
        return self.size

    def read(self, obj):
        size = self.calculate_size(obj)

        # If the size can be determined easily, read
        # that number of bytes and return it directly.
        if self.size is not None:
            return obj.read(self.size)

        # Otherwise, the field needs to supply its own
        # technique for determining how much data to read.
        raise NotImplementedError()

    def write(self, obj, value):
        # By default, this doesn't do much, but individual
        # fields can/should override it if necessary
        obj.write(value)

