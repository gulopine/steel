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


if __name__ == '__main__':
    unittest.main()
