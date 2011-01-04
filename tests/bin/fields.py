import unittest

from biwako.bin.fields import numbers


class EndiannessTests(unittest.TestCase):
    decoded_value = 42

    def test_BigEndian(self):
        field = numbers.Integer(size=2, endianness=numbers.BigEndian())
        encoded_value = b'\x00\x2a'
#        encoded_value = b'\x2a\x00'
        self.assertEqual(field.decode(encoded_value), self.decoded_value)
        self.assertEqual(field.encode(self.decoded_value), encoded_value)

    def test_LittleEndian(self):
        field = numbers.Integer(size=2, endianness=numbers.LittleEndian())
        encoded_value = b'\x2a\x00'
#        encoded_value = b'\x00\x2a'
        self.assertEqual(field.decode(encoded_value), self.decoded_value)
        self.assertEqual(field.encode(self.decoded_value), encoded_value)


if __name__ == '__main__':
    unittest.main()
