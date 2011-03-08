import datetime

from .base import Field
from biwako import args


class Date(Field):
    """
    A field that contains data in the form of dates,
    represented in Python by datetime.date.

    format
        A strptime()-style format string.
        See http://docs.python.org/library/datetime.html for details
    """
    format = args.Argument(default='%Y-%m-%d')

    def decode(self, value):
        """
        Parse a string value according to self.format
        and return only the date portion.
        """
        if isinstance(value, datetime.date):
            return value
        return datetime.datetime.strptime(value, self.format).date()

    def encode(self, value):
        """
        Format a date according to self.format and return that as a string.
        """
        return value.strftime(self.format)


