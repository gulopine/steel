import sys

from ..common import data


class Condition:
    def __init__(self, a, b, compare):
        self.a = a
        self.b = b
        self.compare = compare

    def __enter__(self):
        # Hack to add the condition to the class without
        # having to explicitly give it a (useless) name
        frame = sys._getframe(1)
        locals = frame.f_locals
        locals[self.get_available_name(locals.keys())] = self

        # This has to come after the frame hack, so that the condition gets
        # placed in the outer namespace, not in the inner 'with' block
        data.field_stack.append([])

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

    def attach_to_class(self, cls):
        cls._fields.append(self)

    def __get__(self, instance, owner):
        if not instance:
            return self
        
        if self.name in instance.__dict__:
            # This condition has already been processed, so don't try getting it again
            print('Already been processed')
            return None

        # Customizes the field for this particular instance
        # Use field instead of self for the rest of the method
        a = self.a
        if hasattr(self.a, 'for_instance'):
            a = a.for_instance(instance)
        if hasattr(a, 'resolve'):
            a = a.resolve(instance)

        b = self.b
        if hasattr(self.b, 'for_instance'):
            b = b.for_instance(instance)
        if hasattr(b, 'resolve'):
            b = b.resolve(instance)

        if self.compare(a, b):
            # The comparison succeeded, so the fields should be processed

            raw_bytes = b''
            for field in self.fields:
                field = field.for_instance(instance)
                bytes, value = field.read_value(instance)
                raw_bytes += bytes
                instance.__dict__[field.name] = value
                field.after_decode.apply(instance, value)
            instance._raw_values[self.name] = raw_bytes

        return None


    def __set__(self, instance, value):
        instance.__dict__[self.name] = value
        instance._raw_values[self.name] = b''


