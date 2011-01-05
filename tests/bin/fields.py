import unittest

from biwako.bin import fields


class EndiannessTest(unittest.TestCase):
    decoded_value = 42
    
    def test_BigEndian(self):
        endianness = fields.BigEndian()
        encoded_value = b'\x00*'
        self.assertEqual(endianness.encode(self.decoded_value, size=2), encoded_value)
        self.assertEqual(endianness.decode(encoded_value, size=2), self.decoded_value)

    def test_LittleEndian(self):
        endianness = fields.LittleEndian()
        encoded_value = b'*\x00'
        self.assertEqual(endianness.encode(self.decoded_value, size=2), encoded_value)
        self.assertEqual(endianness.decode(encoded_value, size=2), self.decoded_value)


class SigningTest(unittest.TestCase):
    decoded_value = -42

    def test_SignMagnitude(self):
        signer = fields.SignMagnitude()
        encoded_value = 0b10101010
        self.assertEqual(bin(signer.encode(self.decoded_value, size=1)), bin(encoded_value))
        self.assertEqual(signer.decode(encoded_value, size=1), self.decoded_value)
        # Make sure it doesn't muck up positive values
        self.assertEqual(signer.encode(42, size=1), 42)
        self.assertEqual(signer.decode(42, size=1), 42)

    def test_OnesComplement(self):
        signer = fields.OnesComplement()
        encoded_value = 0b11010101
        self.assertEqual(bin(signer.encode(self.decoded_value, size=1)), bin(encoded_value))
        self.assertEqual(signer.decode(encoded_value, size=1), self.decoded_value)
        # Make sure it doesn't muck up positive values
        self.assertEqual(signer.encode(42, size=1), 42)
        self.assertEqual(signer.decode(42, size=1), 42)

    def test_TwosComplement(self):
        signer = fields.TwosComplement()
        encoded_value = 0b11010110
        self.assertEqual(bin(signer.encode(self.decoded_value, size=1)), bin(encoded_value))
        self.assertEqual(signer.decode(encoded_value, size=1), self.decoded_value)
        # Make sure it doesn't muck up positive values
        self.assertEqual(signer.encode(42, size=1), 42)
        self.assertEqual(signer.decode(42, size=1), 42)


class TestInteger(unittest.TestCase):
    def test_signed(self):
        field = fields.Integer(size=1, signed=True)
        self.assertEqual(field.encode(127), b'\x7f')
        self.assertEqual(field.encode(-127), b'\x81')

        # Values higher than 127 can't be encoded
        with self.assertRaises(ValueError):
            field.encode(128)

    def test_unsigned(self):
        field = fields.Integer(size=1, signed=False)
        self.assertEqual(field.encode(127), b'\x7f')
        self.assertEqual(field.encode(128), b'\x80')

        # Negative values can't be encoded
        with self.assertRaises(ValueError):
            field.encode(-127)

        # Values higher than 255 can't be encoded
        with self.assertRaises(ValueError):
            field.encode(256)


if __name__ == '__main__':
    unittest.main()
