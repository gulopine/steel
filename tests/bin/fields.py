import unittest

from biwako.bin import fields


class EndiannessTest(unittest.TestCase):
    decoded_value = 42
    
    def test_BigEndian(self):
        field = fields.Integer(size=2, endianness=fields.BigEndian())
        encoded_value = b'\x00*'
        self.assertEqual(field.encode(self.decoded_value), encoded_value)
        self.assertEqual(field.decode(encoded_value), self.decoded_value)

    def test_LittleEndian(self):
        field = fields.Integer(size=2, endianness=fields.LittleEndian())
        encoded_value = b'*\x00'
        self.assertEqual(field.encode(self.decoded_value), encoded_value)
        self.assertEqual(field.decode(encoded_value), self.decoded_value)


class SigningTest(unittest.TestCase):
    decoded_value = -42

    def test_SignMagnitude(self):
        signer = fields.SignMagnitude()
        encoded_value = 0b10101010
        self.assertEqual(bin(signer.encode(self.decoded_value, size=1)), bin(encoded_value))
        self.assertEqual(signer.decode(encoded_value, size=1), self.decoded_value)

    def test_OnesComplement(self):
        signer = fields.OnesComplement()
        encoded_value = 0b11010101
        self.assertEqual(bin(signer.encode(self.decoded_value, size=1)), bin(encoded_value))
        self.assertEqual(signer.decode(encoded_value, size=1), self.decoded_value)

    def test_TwosComplement(self):
        signer = fields.TwosComplement()
        encoded_value = 0b11010110
        self.assertEqual(bin(signer.encode(self.decoded_value, size=1)), bin(encoded_value))
        self.assertEqual(signer.decode(encoded_value, size=1), self.decoded_value)


if __name__ == '__main__':
    unittest.main()
