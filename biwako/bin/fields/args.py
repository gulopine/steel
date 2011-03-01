class Argument:
    def __init__(self, positional=False, resolve_field=False, **kwargs):
        self.resolve_field = resolve_field

        # Default can be None, so we have to do some extra work to
        # fall back in the event that no defualt value was provided
        if 'default' in kwargs:
            self.default = kwargs.pop('default')
            self.has_default = True
        else:
            self.default = None
            self.has_default = False

        # Because of all that default mess, we need to make sure kwargs
        # doesn't have any arguments we don't know how to deal with
        if kwargs:
            # Just grab the first one to show in the error message
            raise TypeError('Unknown argument %r' % iter(kwargs).__next__())

    def set_name(self, name):
        self.name = name

    def attach_to_class(self, cls):
        cls.arguments[self.name] = cls


class Override(Argument):
    def __init__(self, **kwargs):
        # For now, just save the arguments for later
        self.overrides = kwargs

    def attach_to_class(self, cls):
        # Replace the original options with any replacements provided
        for name, value in self.overrides.items():
            if name in cls.arguments:
                setattr(cls.arguments[self.name], name, value)
            else:
                raise TypeError("%r is not an argument, so it can't be overridden" % self.name)


class Removed(Argument):
    def __init__(self):
        # Nothing to do for this part of the process, we just
        # need to prevent the normal behavior from taking place
        pass

    def attach_to_class(self, cls):
        # Remove the argument from the class
        try:
            del cls.arguments[self.name]
        except KeyError:
            raise TypeError("%r is not an argument, so it can't be removed" % self.name)


