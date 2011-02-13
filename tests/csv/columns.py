import unittest
import datetime
import decimal

from biwako import csv


class FieldTests(unittest.TestCase):
    invalid_values = []

    def setUp(self):
        self.field = csv.Field()
        self.encoded_value = 'value'
        self.decoded_value = 'value'

    def test_validation(self):
        try:
            self.field.validate(self.decoded_value)
        except ValueError as e:
            self.fail(str(e))

    def test_python_conversion(self):
        decoded_value = self.field.decode(self.encoded_value)
        self.assertEqual(decoded_value, self.decoded_value)

    def test_string_conversion(self):
        encoded_value = str(self.field.encode(self.decoded_value))
        self.assertEqual(encoded_value, self.encoded_value)

    def test_invalid_value(self):
        for value in self.invalid_values:
            try:
                value = self.field.decode(value)
            except ValueError:
                # If it's caught here, there's no need to test anything else
                return
            self.assertRaises(ValueError, self.field.validate, value)


class StringTests(FieldTests):
    def setUp(self):
        self.field = csv.String()
        self.encoded_value = 'value'
        self.decoded_value = 'value'


class IntegerTests(FieldTests):
    def setUp(self):
        self.field = csv.Integer()
        self.encoded_value = '1'
        self.decoded_value = 1
        self.invalid_values = ['invalid']


class FloatTests(FieldTests):
    def setUp(self):
        self.field = csv.Float()
        self.encoded_value = '1.1'
        self.decoded_value = 1.1
        self.invalid_values = ['invalid']


class DecimalTests(FieldTests):
    def setUp(self):
        self.field = csv.Decimal()
        self.encoded_value = '1.1'
        self.decoded_value = decimal.Decimal('1.1')
        self.invalid_values = ['invalid']


class DateTests(FieldTests):
    def setUp(self):
        self.field = csv.Date()
        self.encoded_value = '2010-03-31'
        self.decoded_value = datetime.date(2010, 3, 31)
        self.invalid_values = ['invalid', '03-31-2010']


class FormattedDateTests(FieldTests):
    def setUp(self):
        self.field = csv.Date(format='%m/%d/%Y')
        self.encoded_value = '03/31/2010'
        self.decoded_value = datetime.date(2010, 3, 31)
        self.invalid_values = ['invalid', '03-31-2010']


