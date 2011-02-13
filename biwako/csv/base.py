import csv
import collections

from ..csv import data

__all__ = ['Row', 'Reader', 'Writer']


class NameAwareOrderedDict(collections.OrderedDict):
    """
    A custom namespace that not only orders its items, but can
    also make those items aware of their names immediately.
    """

    def __setitem__(self, name, obj):
        super(NameAwareOrderedDict, self).__setitem__(name, obj)
        if hasattr(obj, 'set_name'):
            obj.set_name(name)


class Dialect:
    def __init__(self, *, has_header_row=False, **kwargs):
        self.has_header_row = has_header_row
        self.csv_dialect = kwargs
        self.fields = []

    def add_field(self, field):
        self.fields.append(field)


class RowMeta(type):
    def __new__(cls, name, bases, attrs, **options):
        # Nothing to do here, but we need to make sure options
        # don't get passed in to type.__new__() itself.
        return type.__new__(cls, name, bases, attrs)

    def __init__(cls, name, bases, attrs, **options):
        cls._fields = []
        for name, attr in attrs.items():
            if hasattr(attr, 'attach_to_class'):
                attr.attach_to_class(cls)
        data.fields.options = {}
        cls._dialect = Dialect(**options)

    @classmethod
    def __prepare__(cls, name, bases):
        return NameAwareOrderedDict()


class Row(metaclass=RowMeta):
    def __init__(self, *args, **kwargs):
        field_names = [field.name for field in self._dialect.fields]

        # First, make sure the arguments make sense
        if len(args) > len(field_names):
            msg = "__init__() takes at most %d arguments (%d given)"
            raise TypeError(msg % (len(field_names), len(args)))

        for name in kwargs:
            if name not in field_names:
                raise TypeError("Got unknown keyword argument '%s'" % name)

        for i, name in enumerate(field_names[:len(args)]):
            if name in kwargs:
                msg = "__init__() got multiple values for keyword argument '%s'"
                raise TypeError(msg % name)
            kwargs[name] = args[i]

        # Now populate the actual values on the object
        for field in self._dialect.fields:
            try:
                value = field.decode(kwargs[field.name])
            except KeyError:
                # No value was provided
                value = None
            setattr(self, field.name, value)

    errors = ()

    def is_valid(self):
        self.errors = []
        for field in self._dialect.fields:
            value = getattr(self, field.name)
            try:
                field.validate(value)
            except ValueError as e:
                self.errors.append(e)
        return not self.errors

    @classmethod
    def reader(cls, file):
        return Reader(cls, file)

    @classmethod
    def writer(cls, file):
        return Writer(cls, file)


class Reader:
    def __init__(self, row_cls, file):
        self.row_cls = row_cls
        self.csv_reader = csv.reader(file, **row_cls._dialect.csv_dialect)
        self.skip_header_row = row_cls._dialect.has_header_row

    def __iter__(self):
        return self

    def __next__(self):
        # Skip the first row if it's a header
        if self.skip_header_row:
            self.csv_reader.__next__()
            self.skip_header_row = False

        return self.row_cls(*self.csv_reader.__next__())


class Writer:
    def __init__(self, row_cls, file):
        self.fields = row_cls._dialect.fields
        self._writer = csv.writer(file, row_cls._dialect.csv_dialect)
        self.needs_header_row = row_cls._dialect.has_header_row

    def writerow(self, row):
        if self.needs_header_row:
            values = [field.label for field in self.fields]
            self._writer.writerow(values)
            self.needs_header_row = False
        values = [getattr(row, fields.name) for field in self.fields]
        self._writer.writerow(values)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


