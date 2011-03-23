class Condition:
    def __init__(self, a, b, compare):
        self.a = a
        self.b = b

    def __enter__(self):
        pass # TODO push a new namespace onto the stack

    def __exit__(self, 	exception_type, exception, traceback):
        pass # TODO pull the namespace off the stack and save it for later

        # Don't suppress the exception, if any
        return False


