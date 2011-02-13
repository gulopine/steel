import decimal

from .base import Field


class Integer(Field):
    def decode(self, value):
        return int(value)


class Float(Field):
    def decode(self, value):
        return float(value)


class Decimal(Field):
    """
    A field that contains data in the form of decimal values,
    represented in Python by decimal.Decimal.
    """

    def decode(self, value):
        try:
            return decimal.Decimal(value)
        except decimal.InvalidOperation as e:
            raise ValueError(str(e))


