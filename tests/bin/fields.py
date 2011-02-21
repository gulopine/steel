import io
import unittest

from biwako.bin import fields, Structure


class IOTest(unittest.TestCase):
    data = b'\x2a\x42'

    def setUp(self):
        self.input = io.BytesIO(b'\x2a\x42')
        self.output = io.BytesIO()

    def test_read(self):
        # If no size is provided, a simple field can't be read.
        field = fields.Field()
        with self.assertRaises(NotImplementedError):
            field.read(self.input)

        field = fields.Field(size=2)
        data = field.read(self.input)
        self.assertEqual(data, self.data)

    def test_write(self):
        field = fields.Field(size=2)
        field.write(self.output, self.data)
        self.assertEqual(self.output.getvalue(), self.data)


class EndiannessTest(unittest.TestCase):
    decoded_value = 42
    
    def test_BigEndian(self):
        endianness = fields.BigEndian(size=2)
        encoded_value = b'\x00*'
        self.assertEqual(endianness.encode(self.decoded_value), encoded_value)
        self.assertEqual(endianness.decode(encoded_value), self.decoded_value)

    def test_LittleEndian(self):
        endianness = fields.LittleEndian(size=2)
        encoded_value = b'*\x00'
        self.assertEqual(endianness.encode(self.decoded_value), encoded_value)
        self.assertEqual(endianness.decode(encoded_value), self.decoded_value)


class SigningTest(unittest.TestCase):
    decoded_value = -42

    def test_SignMagnitude(self):
        signer = fields.SignMagnitude(size=1)
        encoded_value = 0b10101010
        self.assertEqual(bin(signer.encode(self.decoded_value)), bin(encoded_value))
        self.assertEqual(signer.decode(encoded_value), self.decoded_value)
        # Make sure it doesn't muck up positive values
        self.assertEqual(signer.encode(42), 42)
        self.assertEqual(signer.decode(42), 42)

    def test_OnesComplement(self):
        signer = fields.OnesComplement(size=1)
        encoded_value = 0b11010101
        self.assertEqual(bin(signer.encode(self.decoded_value)), bin(encoded_value))
        self.assertEqual(signer.decode(encoded_value), self.decoded_value)
        # Make sure it doesn't muck up positive values
        self.assertEqual(signer.encode(42), 42)
        self.assertEqual(signer.decode(42), 42)

    def test_TwosComplement(self):
        signer = fields.TwosComplement(size=1)
        encoded_value = 0b11010110
        self.assertEqual(bin(signer.encode(self.decoded_value)), bin(encoded_value))
        self.assertEqual(signer.decode(encoded_value), self.decoded_value)
        # Make sure it doesn't muck up positive values
        self.assertEqual(signer.encode(42), 42)
        self.assertEqual(signer.decode(42), 42)


class TestInteger(unittest.TestCase):
    def test_signed(self):
        field = fields.Integer(size=1, signed=True)
        self.assertEqual(field.encode(None, 127), b'\x7f')
        self.assertEqual(field.encode(None, -127), b'\x81')

        # Values higher than 127 can't be encoded
        with self.assertRaises(ValueError):
            field.encode(None, 128)

    def test_unsigned(self):
        field = fields.Integer(size=1, signed=False)
        self.assertEqual(field.encode(None, 127), b'\x7f')
        self.assertEqual(field.encode(None, 128), b'\x80')

        # Negative values can't be encoded
        with self.assertRaises(ValueError):
            field.encode(None, -127)

        # Values higher than 255 can't be encoded
        with self.assertRaises(ValueError):
            field.encode(None, 256)


class TestFixedInteger(unittest.TestCase):
    def test(self):
        field = fields.FixedInteger(42, size=1)
        self.assertEqual(field.encode(None, 42), b'\x2a')
        self.assertEqual(field.decode(b'\x2a'), 42)

        with self.assertRaises(ValueError):
            field.encode(None, 43)

        with self.assertRaises(ValueError):
            field.decode(b'\x2b')


class CalculatedValueTest(unittest.TestCase):
    def setUp(self):
        self.field = fields.Integer(size=1)
        self.name = 'test'

    def test_add(self):
        calc_field = self.field + 2
        self.assertEqual(calc_field.extract(io.BytesIO(b'\x2a')), 44)
        calc_field = 2 + self.field
        self.assertEqual(calc_field.extract(io.BytesIO(b'\x2a')), 44)

    def test_subtract(self):
        calc_field = self.field - 2
        self.assertEqual(calc_field.extract(io.BytesIO(b'\x2a')), 40)
        calc_field = 42 - self.field
        self.assertEqual(calc_field.extract(io.BytesIO(b'\x02')), 40)

    def test_multiply(self):
        calc_field = self.field * 2
        self.assertEqual(calc_field.extract(io.BytesIO(b'\x2a')), 84)
        calc_field = 2 * self.field
        self.assertEqual(calc_field.extract(io.BytesIO(b'\x2a')), 84)

    def test_power(self):
        calc_field = self.field ** 2
        self.assertEqual(calc_field.extract(io.BytesIO(b'\x2a')), 1764)
        calc_field = 2 ** self.field
        self.assertEqual(calc_field.extract(io.BytesIO(b'\x10')), 65536)

    def test_true_divide(self):
        calc_field = self.field / 2
        self.assertEqual(calc_field.extract(io.BytesIO(b'\x2a')), 21)
        calc_field = 42 / self.field
        self.assertEqual(calc_field.extract(io.BytesIO(b'\x02')), 21)

    def test_floor_divide(self):
        calc_field = self.field // 2
        self.assertEqual(calc_field.extract(io.BytesIO(b'\x2a')), 21)
        calc_field = 42 // self.field
        self.assertEqual(calc_field.extract(io.BytesIO(b'\x02')), 21)

    def test_chaining(self):
        calc_field = self.field + 2 + 2
        self.assertEqual(calc_field.extract(io.BytesIO(b'\x2a')), 46)
        calc_field = (self.field + 2 - 2) * 5 // 4
        self.assertEqual(calc_field.extract(io.BytesIO(b'\x2a')), 52)


class StringTest(unittest.TestCase):
    def test_ascii(self):
        field = fields.String(encoding='ascii')
        self.assertEqual(field.encode(None, 'test'), b'test\x00')
        self.assertEqual(field.extract(io.BytesIO(b'test\x00')), 'test')
        
        # Most Unicode can't be encoded in ASCII
        with self.assertRaises(ValueError):
            field.encode(None, '\u00fcber')

    def test_utf8(self):
        field = fields.String(encoding='utf8')
        self.assertEqual(field.encode(None, '\u00fcber'), b'\xc3\xbcber\x00')
        self.assertEqual(field.extract(io.BytesIO(b'\xc3\xbcber\x00')), '\u00fcber')

    def test_invalid_encoding(self):
        with self.assertRaises(TypeError):
            fields.String()
        with self.assertRaises(LookupError):
            fields.String(encoding='invalid')


class LengthIndexedString(unittest.TestCase):
    encoded_data = b'\x05valid'
    decoded_data = 'valid'

    def setUp(self):
        self.field = fields.LengthIndexedString(size=1, encoding='ascii')

    def test_encode(self):
        self.assertEqual(self.field.encode(None, self.decoded_data), self.encoded_data)

    def test_extract(self):
        file = io.BytesIO(self.encoded_data)
        self.assertEqual(self.field.extract(file), self.decoded_data)


class FixedStringTest(unittest.TestCase):
    def test_bytes(self):
        field = fields.FixedString(b'valid')
        field.encode(None, b'valid')
        field.extract(io.BytesIO(b'valid'))

        with self.assertRaises(ValueError):
            field.extract(io.BytesIO(b'invalid'))

        # Encoding a Unicode string isn't possible with a bytes FixedString
        with self.assertRaises(ValueError):
            field.extract(io.TextIOBase('valid'))

    def test_ascii(self):
        field = fields.FixedString('valid')
        field.encode(None, 'valid')
        field.extract(io.BytesIO(b'valid'))

        with self.assertRaises(ValueError):
            field.encode(None, 'invalid')

        with self.assertRaises(ValueError):
            field.extract(io.BytesIO(b'invalid'))

    def test_utf8(self):
        field = fields.FixedString('\u00fcber', encoding='utf8')
        field.encode(None, '\u00fcber')
        field.extract(io.BytesIO(b'\xc3\xbcber'))

        # If the value doesn't match what was specified, it's an error
        with self.assertRaises(ValueError):
            field.encode(None, 'uber')

        with self.assertRaises(ValueError):
            field.extract(io.BytesIO(b'uber'))


class BytesTest(unittest.TestCase):
    data = b'\x42\x00\x2a'

    def test_encode(self):
        field = fields.Bytes(size=3)
        self.assertEqual(field.encode(None, self.data), self.data)

    def test_extract(self):
        field = fields.Bytes(size=3)
        self.assertEqual(field.extract(io.BytesIO(self.data)), self.data)


class ListTest(unittest.TestCase):
    encoded_data = b'\x42\x52\x2a\x3a'
    decoded_data = [66, 82, 42, 58]

    def setUp(self):
        self.field = fields.List(fields.Integer(size=1), size=4)

    def test_encode(self):
        data = self.field.encode(None, self.decoded_data)
        self.assertEqual(data, self.encoded_data)

    def test_extract(self):
        data = self.field.extract(io.BytesIO(self.encoded_data))
        self.assertSequenceEqual(data, self.decoded_data)


class ZlibTest(unittest.TestCase):
    encoded_data = b'x\x9c+I-.\x01\x00\x04]\x01\xc1'
    decoded_data = 'test'

    def setUp(self):
        self.field = fields.Zlib(fields.String(size=4, encoding='ascii'), size=fields.Remainder)

    def test_encode(self):
        data = self.field.encode(None, self.decoded_data)
        self.assertEqual(data, self.encoded_data)

    def test_extract(self):
        data = self.field.extract(io.BytesIO(self.encoded_data))
        self.assertSequenceEqual(data, self.decoded_data)


class CheckSumTest(unittest.TestCase):
    original_data = b'\x00\x01\x02\x03\x00\x04\x00\x00\x00\x05\x00\x0f'
    modified_data = b'\x00\x02\x02\x03\x00\x04\x00\x00\x00\x05\x00\x0f'
    modified_csum = b'\x00\x01\x02\x03\x00\x04\x00\x00\x00\x05\x00\x10'
    modified_both = b'\x00\x02\x02\x03\x00\x04\x00\x00\x00\x05\x00\x10'

    class IntegrityStructure(Structure):
        a = fields.Integer(size=2)
        b = fields.Integer(size=1)
        c = fields.Integer(size=1)
        d = fields.Integer(size=2)
        e = fields.Integer(size=4)
        checksum = fields.CheckSum(size=2)

    def test_encode(self):
        pass
#        data = self.field.encode(None, self.decoded_data)
#        self.assertEqual(data, self.encoded_data)

    def test_extract(self):
        struct = self.IntegrityStructure(io.BytesIO(self.original_data))
        self.assertEqual(struct.a, 1)
        self.assertEqual(struct.b, 2)
        self.assertEqual(struct.c, 3)
        self.assertEqual(struct.d, 4)
        self.assertEqual(struct.e, 5)
        self.assertEqual(struct.checksum, 15)

    def test_modified_data(self):
        struct = self.IntegrityStructure(io.BytesIO(self.modified_data))
        with self.assertRaises(fields.IntegrityError):
            self.assertNotEqual(struct.checksum, 15)

    def test_modified_both(self):
        struct = self.IntegrityStructure(io.BytesIO(self.original_data))
        self.assertEqual(struct.a, 1)
        self.assertEqual(struct.b, 2)
        self.assertEqual(struct.c, 3)
        self.assertEqual(struct.d, 4)
        self.assertEqual(struct.e, 5)
        struct.a = 2
        data = io.BytesIO()
        struct.save(data)
        self.assertEqual(data.getvalue(), self.modified_both)

    def test_modified_checksum(self):
        struct = self.IntegrityStructure(io.BytesIO(self.modified_csum))
        with self.assertRaises(fields.IntegrityError):
            self.assertNotEqual(struct.checksum, 15)


class ReservedTest(unittest.TestCase):
    class ReservedStructure(Structure):
        a = fields.Integer(size=1)
        fields.Reserved(size=1)
        b = fields.Integer(size=1)
    data = b'\x01\x00\x02'

    def test_assignment(self):
        # Giving no name is the correct approach
        class ReservedStructure(Structure):
            fields.Reserved(size=1)

        with self.assertRaises(TypeError):
            class ReservedStructure(Structure):
                name = fields.Reserved(size=1)

    def test_read(self):
        obj = self.ReservedStructure(io.BytesIO(self.data))
        self.assertEqual(obj.a, 1)
        self.assertEqual(obj.b, 2)

    def test_save(self):
        obj = self.ReservedStructure(io.BytesIO())
        obj.a = 1
        obj.b = 2
        data = io.BytesIO()
        obj.save(data)
        self.assertEqual(data.getvalue(), self.data)


if __name__ == '__main__':
    unittest.main()
