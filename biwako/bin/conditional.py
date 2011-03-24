import sys

from ..common import data

class Condition:
    def __init__(self, a, b, compare):
        self.a = a
        self.b = b

    def __enter__(self):
        data.field_stack.append([])

        # Hack to add the condition to the class without
        # having to explicitly give it a (useless) name
        frame = sys._getframe(1)
        locals = frame.f_locals
        locals[self.get_available_name(locals.keys())] = self

        # Return it anyway, just to check if someone does try to give it a name
        return self

    def __exit__(self, 	exception_type, exception, traceback):
        self.fields = data.field_stack.pop()

        # Don't suppress the exception, if any
        return False

    def get_available_name(self, locals):
        i = 0
        while True:
            name = '_condition_%s' % i
            if name not in locals:
                return name
            i += 1

    def set_name(self, name):
        if hasattr(self, 'name'):
            raise TypeError('Field conditions must not use the "as" form')
        self.name = name

