import io
import unittest

import steel


class AttributeTest(unittest.TestCase):
    def setUp(self):
        class TestStructure(steel.Structure):
            integer = steel.Integer('number', size=1)
            string = steel.String(encoding='ascii')
            
        self.struct = TestStructure

    def test_order(self):
        f1, f2 = self.struct._fields.values()
        self.assertEqual(type(f1), steel.Integer)
        self.assertEqual(type(f2), steel.String)

    def test_names(self):
        f1, f2 = self.struct._fields.values()
        self.assertEqual(f1.name, 'integer')
        self.assertEqual(f2.name, 'string')

    def test_labels(self):
        f1, f2 = self.struct._fields.values()
        self.assertEqual(f1.label, 'Number')
        self.assertEqual(f2.label, 'String')

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
            
    def test_related(self):
        class TestStructure(steel.Structure):
            length = steel.Integer('number', size=1)
            content = steel.String(encoding='ascii', size=length)
        
        struct = TestStructure(io.BytesIO(b'\x05validpadding'))
        self.assertEqual(struct.length, 5)
        self.assertEqual(struct.content, 'valid')
        
        struct.content = 'automatic'
        self.assertEqual(struct.content, 'automatic')
        self.assertEqual(struct.length, 9)

class IOTest(unittest.TestCase):
    data = b'\x2a\x00\x42valid\x00test\x00'

    def setUp(self):
        self.input = io.BytesIO(self.data)
        self.output = io.BytesIO()
        
        class TestStructure(steel.Structure):
            forty_two = steel.Integer(size=2, endianness=steel.LittleEndian)
            sixty_six = steel.Integer(size=1)
            valid = steel.String(encoding='ascii')
            test = steel.String(encoding='ascii')

        self.struct = TestStructure

    def test_mode(self):
        struct = self.struct(self.input)
        self.assertEqual(struct._mode, 'rb')

        struct = self.struct()
        self.assertEqual(struct._mode, 'wb')

    def test_read(self):
        struct = self.struct(self.input)
        self.assertEqual(struct.read(), self.data)

    def test_write(self):
        struct = self.struct()
        struct.write(self.data)
        self.assertEqual(struct.forty_two, 42)
        self.assertEqual(struct.sixty_six, 66)
        self.assertEqual(struct.valid, 'valid')
        self.assertEqual(struct.test, 'test')

        # Writing just part of the data populates some of the fields
        struct = self.struct()
        struct.write(self.data[:6])
        self.assertEqual(struct.forty_two, 42)
        self.assertEqual(struct.sixty_six, 66)
        with self.assertRaises(AttributeError):
            struct.valid

        # Writing more will populate more fields
        struct.write(self.data[6:12])
        self.assertEqual(struct.forty_two, 42)
        self.assertEqual(struct.sixty_six, 66)
        self.assertEqual(struct.valid, 'valid')
        with self.assertRaises(AttributeError):
            struct.test

        # Finishing up the data populates the rest of the fields
        struct.write(self.data[12:])
        self.assertEqual(struct.forty_two, 42)
        self.assertEqual(struct.sixty_six, 66)
        self.assertEqual(struct.valid, 'valid')
        self.assertEqual(struct.test, 'test')

    def test_attributes(self):
        struct = self.struct(io.BytesIO(self.data))
        self.assertEqual(struct.forty_two, 42)
        self.assertEqual(struct.sixty_six, 66)
        self.assertEqual(struct.valid, 'valid')
        self.assertEqual(struct.test, 'test')

        # Now test them again in a random order
        struct = self.struct(io.BytesIO(self.data))
        self.assertEqual(struct.valid, 'valid')
        self.assertEqual(struct.forty_two, 42)
        self.assertEqual(struct.test, 'test')
        self.assertEqual(struct.sixty_six, 66)

    def test_save(self):
        struct = self.struct()
        struct.forty_two = 42
        struct.sixty_six = 66
        struct.valid = 'valid'
        struct.test = 'test'

        output = io.BytesIO()
        struct.save(output)
        self.assertEqual(output.getvalue(), self.data)

    def test_read_and_save(self):
        struct = self.struct(io.BytesIO(self.data))

        output = io.BytesIO()
        struct.save(output)
        self.assertEqual(output.getvalue(), self.data)


class OptionsTest(unittest.TestCase):
    def test_arguments(self):
        class TestStructure(steel.Structure, attribute='test'):
            pass


if __name__ == '__main__':
    unittest.main()
