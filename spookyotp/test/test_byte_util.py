import unittest
from spookyotp.byte_util import (int_to_bytearray,
                                 bytes_to_31_bit_int)


class TestByteUtil(unittest.TestCase):
    """
    Tests for the byte-manipulation utilities
    """
    def test_int_to_bytearray(self):
        """
        int_to_bytearray should convert ints to byte arrays
        """
        self.assertEqual(int_to_bytearray(0),
                         b'\x00\x00\x00\x00\x00\x00\x00\x00')
        self.assertEqual(int_to_bytearray(2**64 - 1),
                         b'\xff\xff\xff\xff\xff\xff\xff\xff')
        self.assertEqual(int_to_bytearray(17848395054321),
                         b'\x00\x00\x10\x3b\xa7\x3f\x3c\xf1')

    def test_int_to_bytearray_raises(self):
        """
        int_to_bytearray should raise for non-uint64 values
        """
        self.assertRaises(ValueError, int_to_bytearray, 2**64)
        self.assertRaises(ValueError, int_to_bytearray, -1)
        self.assertRaises(TypeError, int_to_bytearray, 12.34)
        self.assertRaises(TypeError, int_to_bytearray, '2134')

    def test_bytes_to_31_bit_int(self):
        """
        bytes_to_31_bit_int should convert bytes to ints
        while truncating higher bits
        """
        self.assertEqual(bytes_to_31_bit_int(b'\x00'), 0)
        self.assertEqual(bytes_to_31_bit_int(b'\x77\x11\xaa\xff'), 1997646591)
        self.assertEqual(bytes_to_31_bit_int(b'\x88\x11\xaa\xff'), 135375615)
        self.assertEqual(bytes_to_31_bit_int(b'\xff'*8), 2**31 - 1)
        self.assertEqual(bytes_to_31_bit_int(bytearray(b'\x77\x11\xaa\xff')),
                         1997646591)


if __name__ == '__main__':
    unittest.main()
