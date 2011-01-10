import io
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


class IOTest(unittest.TestCase):
    data = b'\x2a\x00\x42valid'

    def setUp(self):
        self.input = io.BytesIO(self.data)
        self.output = io.BytesIO()
        
        class TestStructure(bin.Structure):
            forty_two = bin.Integer(size=2, endianness=bin.LittleEndian())
            sixty_six = bin.Integer(size=1)
            string = bin.String(encoding='ascii')

        self.struct = TestStructure

    def test_mode(self):
        struct = self.struct(self.input)
        self.assertEqual(struct.mode, 'rb')

        struct = self.struct()
        self.assertEqual(struct.mode, 'wb')

    def test_read(self):
        struct = self.struct(self.input)
        self.assertEqual(struct.read(10), self.data)

    def test_write(self):
        struct = self.struct()
        struct.write(self.data)



