from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import


__all__ = ['int_to_bytearray', 'bytes_to_31_bit_int']


def int_to_bytearray(number):
    """
    Return a bytearray representation of 64-bit number.
    """
    try:
        if number.bit_length() > 64:
            raise ValueError("Number must be less than {}".format(2**64))
    except AttributeError:
        raise TypeError("Number must be an integer.")
    if number < 0:
        raise ValueError("Number must be greater than 0.")
    mask = 0xff
    shifts = (8*i for i in range(7, -1, -1))
    result = []
    for shift in shifts:
        result.append((number >> shift) & mask)
    return bytearray(result)


def bytes_to_31_bit_int(as_bytes):
    """
    Convert the 31 least-signficant bits to an integer,
    truncating any more significant bits.
    """
    as_bytes = bytearray(as_bytes)
    if len(as_bytes) < 4:
        pad_len = 4 - len(as_bytes)
        as_bytes = bytearray(pad_len * [0]) + as_bytes
    as_int = (((as_bytes[-4] & 0x7f) << 3*8) +
               (as_bytes[-3] << 2*8) +
               (as_bytes[-2] << 1*8) +
               (as_bytes[-1] << 0*8))
    return as_int
