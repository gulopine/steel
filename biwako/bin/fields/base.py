class Field:
    def __init__(self, label=None, size=None):
        self.label = label
        self.size = size

    def calculate_size(self):
        return self.size
