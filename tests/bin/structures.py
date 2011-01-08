import unittest

from biwako import bin


class AttributeTest(unittest.TestCase):
    def setUp(self):
        class TestStructure(bin.Structure):
            integer = bin.Integer('number', size=1)
            string = bin.String(encoding='ascii')
            
        self.struct = TestStructure

    def test_order(self):
        self.assertEqual(type(self.struct._fields[0]), bin.Integer)
        self.assertEqual(type(self.struct._fields[1]), bin.String)

    def test_names(self):
        self.assertEqual(self.struct._fields[0].name, 'integer')
        self.assertEqual(self.struct._fields[1].name, 'string')

    def test_labels(self):
        self.assertEqual(self.struct._fields[0].label, 'Number')
        self.assertEqual(self.struct._fields[1].label, 'String')

