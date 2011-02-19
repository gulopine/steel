import collections
import threading


class NameAwareOrderedDict(collections.OrderedDict):
    """
    A custom namespace that not only orders its items, but can
    also make those items aware of their names immediately.
    """

    def __setitem__(self, name, obj):
        super(NameAwareOrderedDict, self).__setitem__(name, obj)
        if hasattr(obj, 'set_name'):
            obj.set_name(name)


class DeclarativeMetaclass(type):
    def __new__(cls, name, bases, attrs, **options):
        # Nothing to do here, but we need to make sure options
        # don't get passed in to type.__new__() itself.
        return type.__new__(cls, name, bases, attrs)

    def __init__(cls, name, bases, attrs, **options):
        cls._fields = []
        for name, attr in attrs.items():
            if hasattr(attr, 'attach_to_class'):
                attr.attach_to_class(cls)
        data.field_options = {}

    @classmethod
    def __prepare__(cls, name, bases, **options):
        data.field_options = options
        return NameAwareOrderedDict()


class DeclarativeFieldMetaclass(type):
    def __call__(cls, *args, **kwargs):
        if data.field_options:
            options = data.field_options.copy()
            options.update(kwargs)
        else:
            options = kwargs
        return super(DeclarativeFieldMetaclass, cls).__call__(*args, **options)


# Temporary storage
data = threading.local()
data.field_options = {}
