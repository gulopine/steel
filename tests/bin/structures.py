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

    def test_assignment(self):
        struct = self.struct()
        struct.integer = 37
        struct.string = 'still valid'
        self.assertEqual(struct.integer, 37)
        self.assertEqual(struct.string, 'still valid')

        struct = self.struct(integer=42, string='valid')
        self.assertEqual(struct.integer, 42)
        self.assertEqual(struct.string, 'valid')

        with self.assertRaises(TypeError):
            struct = self.struct(io.BytesIO(), integer=1, string='invalid')

class IOTest(unittest.TestCase):
    data = b'\x2a\x00\x42valid'

    def setUp(self):
        self.input = io.BytesIO(self.data)
        self.output = io.BytesIO()
        
        class TestStructure(bin.Structure):
            forty_two = bin.Integer(size=2, endianness=bin.LittleEndian)
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

    def test_attributes(self):
        struct = self.struct(io.BytesIO(self.data))
        self.assertEqual(struct.forty_two, 42)
        self.assertEqual(struct.sixty_six, 66)
        self.assertEqual(struct.string, 'valid')


class OptionsTest(unittest.TestCase):
    def test_arguments(self):
        class TestStructure(bin.Structure, attribute='test'):
#        class TestStructure(bin.Structure):
            pass


