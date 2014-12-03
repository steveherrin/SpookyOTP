import unittest
import mock
import sys
import hashlib
from spookyotp.otp import (OTPBase,
                           HOTP,
                           TOTP,
                           get_random_secret)

class TestSecretUtils(unittest.TestCase):
    """ Test utility functions for the secret.
    """
    def test_get_random_secret_returns_bytearray(self):
        """
        get_random_secret should return a bytearray
        """
        secret = get_random_secret()
        self.assertIsInstance(secret, bytearray)

    @mock.patch('spookyotp.otp.urandom')
    def test_get_random_secret_uses_urandom(self, mock_urandom):
        """
        get_random_secret should use /dev/urandom
        """
        mock_urandom.side_effect = lambda l: b'\x00'*l
        secret = get_random_secret(4)
        mock_urandom.assert_called_once_with(4)
        self.assertEqual(secret, b'\x00\x00\x00\x00')

    def test_get_random_secret_length(self):
        """
        get_random_secret should return arbitrary length secrets
        """
        for l in (10, 20, 30):
            secret = get_random_secret(l)
            self.assertEqual(len(secret), l)


class TestOTPBase(unittest.TestCase):
    @mock.patch('spookyotp.otp.hashlib')
    def test_get_algorithm(self, mock_hashlib):
        """
        Test looking up algorithms in hashlib
        """
        sha1 = OTPBase._get_algorithm('sha1')
        self.assertIs(sha1, mock_hashlib.sha1)

    @mock.patch('spookyotp.otp.hashlib', spec=object)
    def test_get_algorithm_raises(self, mock_hashlib):
        """
        Test that algorithm lookup raises if algorithm isn't found
        """
        self.assertRaises(ValueError, OTPBase._get_algorithm, 'sha1')

    def _test_get_uri(self):
        """
        Test generating the provisioning URL

        Should be otpauth://{t|h}otp/ISSUER:ACCOUNT?secret=B32SECRET&
                                                    issuer=issuer&
                                                    digits=DIGITS&
                                                    algorithm=ALGORITHM&
                                                    counter=COUNTER
                                                 or period=PERIOD
        """
        secret = b'\x11\x22\x33\x44\x55\x66\x77\x88\x99\xaa'
        issuer = 'test'
        account = 'test_user'
        n_digits = 7
        algorithm = 'sha256'

        uri = OTPBase._get_uri(secret, issuer, account, n_digits, algorithm)
        self.assertEqual(uri[:10], "otpauth://")

        protocol, rest = uri[10:].split('/', 1)
        self.assertEqual(protocol, OTPBase._protocol)

        self.assertEqual(rest[:15], "test:test_user?")

        params = rest[15:].split('&')
        import base64
        self.assertIn("secret={}".format(base64.b32encode(secret)), params)
        self.assertIn("issuer={}".format(issuer), params)
        self.assertIn("digits={}".format(n_digits), params)
        self.assertIn("algorithm={}".format(algorithm), params)

    def test_get_otp(self):
        """
        Verify the algorithm to generate the OTP works properly
        """
        self.assertEqual(
            '328482',
            OTPBase._get_otp(bytearray([0]*10), 0, 6, hashlib.sha1))
        self.assertEqual(
            '08683298',
            OTPBase._get_otp(bytearray([255]*10), 1, 8, hashlib.sha1))
        self.assertEqual(
            '000127',
            OTPBase._get_otp(bytearray([42]*19), 1, 6, hashlib.md5))

    def test_get_otp_raises(self):
        """
        Verify the OTP algorithm raises when passed a too-big counter
        """
        self.assertRaises(
            ValueError,
            OTPBase._get_otp, bytearray([0]*10), 2**64, 6, hashlib.sha1)

    def test_compare(self):
        """
        Test _compare correctly compares two differnt OTP codes
        """
        self.assertTrue(OTPBase._compare('123456', '123456'))
        self.assertTrue(OTPBase._compare('234567', u'234567'))
        self.assertFalse(OTPBase._compare('001234', '1234'))
        self.assertFalse(OTPBase._compare('123456', '678901'))

    def test_compare_raises(self):
        """
        _compare should raise if passed invalid OTP codes
        """
        self.assertRaises(ValueError, OTPBase._compare, 'a1b1c2', '123456')
        self.assertRaises(ValueError, OTPBase._compare, '123456', 'g5\\912')
        self.assertRaises(ValueError, OTPBase._compare, '1.23e3', '123456')


class CommonOTPTests(object):
    @mock.patch('spookyotp.otp.qrcode.make')
    def test_get_qr_code(self, mock_make):
        """
        Test getting a QR code for the OTP generator
        """
        self.otp.get_uri = lambda: "otp://otp/TEST_URL"
        mock_img = mock.Mock()
        mock_make.return_value = mock_img

        qr_code = self.otp.get_qr_code()
        mock_make.assert_called_with("otp://otp/TEST_URL")
        self.assertIs(qr_code, mock_img)

    def test_save_qr_code(self):
        """
        Test saving a QR code to a file for the OTP generator
        """
        mock_code = mock.Mock()
        self.otp.get_qr_code = lambda: mock_code

        self.otp.save_qr_code('test.png')
        mock_code.save.assert_called_once_with('test.png')

    @mock.patch('spookyotp.otp.OTPBase._get_uri')
    def test_get_uri(self, mock_get_uri):
        """
        Test getting a provisioning URL (used by QR code)
        """
        mock_get_uri.return_value = 'otpauth://TEST_URL'
        uri = self.otp.get_uri()
        mock_get_uri.assert_called_once_with(self.secret, self.issuer,
                                             self.account, self.n_digits,
                                             self.algorithm,
                                             **self.other_uri_params)
        self.assertEqual(uri, 'otpauth://TEST_URL')

    def test_compare_raises_on_negative(self):
        """
        Test compare raises when passed a negative look-ahead/around
        """
        self.assertRaises(ValueError, self.otp.compare, '000000', -1)


class TestHOTP(unittest.TestCase, CommonOTPTests):
    def setUp(self):
        self.secret = bytearray(b'\x17\r\xc4.\xca\xe8\x1c\x88\xbaB')
        self.issuer = 'test'
        self.account = 'test_user'
        self.n_digits = 6
        self.algorithm = 'sha1'
        self.counter = 1234
        self.other_uri_params = dict(counter=self.counter)
        self.otp = HOTP(self.secret, self.issuer, self.account,
                        self.n_digits, self.algorithm, self.counter)

    @mock.patch('spookyotp.otp.OTPBase._get_otp')
    def test_get_otp_passed_counter(self, mock_get_otp):
        """
        Test get_otp works when passed a particular counter value
        """
        mock_get_otp.return_value = '123456'
        otp = self.otp.get_otp(1001)
        mock_get_otp.assert_called_with(self.secret, 1001, self.n_digits,
                                        getattr(hashlib, self.algorithm))
        self.assertEqual(otp, '123456')
        # counter should not be incremented
        self.assertEqual(self.otp.counter, self.counter)

    @mock.patch('spookyotp.otp.OTPBase._get_otp')
    def test_get_otp(self, mock_get_otp):
        """
        Test get_otp works using the internal counter and increments it
        """
        mock_get_otp.return_value = '123456'
        otp = self.otp.get_otp()
        mock_get_otp.assert_called_with(self.secret, self.counter,
                                        self.n_digits,
                                        getattr(hashlib, self.algorithm))
        self.assertEqual(otp, '123456')
        # counter should be incremented automatically
        self.assertEqual(self.otp.counter, self.counter + 1)

    @mock.patch('spookyotp.otp.OTPBase._get_otp')
    def test_get_otp_no_autoincrement(self, mock_get_otp):
        """
        Test get_otp works using the internal counter but doesn't
        increment it if auto_increment is false.
        """
        mock_get_otp.return_value = '123456'
        otp = self.otp.get_otp(auto_increment=False)
        mock_get_otp.assert_called_with(self.secret, self.counter,
                                        self.n_digits,
                                        getattr(hashlib, self.algorithm))
        self.assertEqual(otp, '123456')
        # counter should be incremented automatically
        self.assertEqual(self.otp.counter, self.counter)

    def test_compare_no_lookahead(self):
        """
        Test compare returns True if the codes are identical
        """
        self.otp.get_otp = lambda counter: str(counter)

        self.assertTrue(self.otp.compare(str(self.counter), 0))
        # should increment the counter to keep in sync
        self.assertEqual(self.otp.counter, self.counter + 1)

    def test_compare_lookahead(self):
        """
        Test compare returns True if the code is in the next few
        """
        self.otp.get_otp = lambda counter: str(counter)

        self.assertTrue(self.otp.compare(str(self.counter + 5), 5))
        # should increment the counter to keep in sync
        self.assertEqual(self.otp.counter, self.counter + 6)

    def test_compare_lookahead_false(self):
        """
        Test compare returns False if the code is not correct
        """
        self.otp.get_otp = lambda counter: str(counter)

        self.assertFalse(self.otp.compare(str(self.counter - 1), 0))
        self.assertEqual(self.otp.counter, self.counter)
        self.assertFalse(self.otp.compare(str(self.counter + 6), 5))
        self.assertEqual(self.otp.counter, self.counter)



class TestTOTP(unittest.TestCase, CommonOTPTests):
    def setUp(self):
        self.secret = bytearray(b'\x17\r\xc4.\xca\xe8\x1c\x88\xbaB')
        self.issuer = 'test'
        self.account = 'test_user'
        self.n_digits = 6
        self.algorithm = 'sha1'
        self.period = 30
        self.time_source = lambda: 1414782000
        self.other_uri_params = dict(period=self.period)
        self.otp = TOTP(self.secret, self.issuer, self.account,
                        self.n_digits, self.algorithm, self.period,
                        time_source=self.time_source)

    @mock.patch('spookyotp.otp.OTPBase._get_otp')
    def test_get_otp_passed_timestamp(self, mock_get_otp):
        """
        Test get_otp works when passed a particular timestamp
        """
        mock_get_otp.return_value = '123456'
        otp = self.otp.get_otp(1414695600)
        counter = 1414695600 // self.period
        mock_get_otp.assert_called_with(self.secret, counter, self.n_digits,
                                        getattr(hashlib, self.algorithm))
        self.assertEqual(otp, '123456')

    @mock.patch('spookyotp.otp.OTPBase._get_otp')
    def test_get_otp(self, mock_get_otp):
        """
        Test get_otp works using the current timestamp
        """
        mock_get_otp.return_value = '123456'
        otp = self.otp.get_otp()
        counter = self.time_source() // self.period
        mock_get_otp.assert_called_with(self.secret, counter,
                                        self.n_digits,
                                        getattr(hashlib, self.algorithm))
        self.assertEqual(otp, '123456')

    def test_compare_no_other_steps(self):
        """
        Test compare returns True if the codes match right now
        """
        self.otp.get_otp = lambda counter: str(counter // self.period)
        correct = str(self.time_source() // self.period)

        self.assertTrue(self.otp.compare(correct, 0))

    def test_compare_nearby_steps(self):
        """
        Test compare returns True if the codes match within a few timesteps
        """
        self.otp.get_otp = lambda counter: str(counter // self.period)
        one_before = str((self.time_source() - self.period) // self.period)
        one_after = str((self.time_source() - self.period) // self.period)

        self.assertTrue(self.otp.compare(one_before, 1))
        self.assertTrue(self.otp.compare(one_after, 1))

    def test_compare_false(self):
        """
        Test compare returns False if the codes don't match
        """
        self.otp.get_otp = lambda counter: str(counter // self.period)
        two_before = str((self.time_source() - 2*self.period) // self.period)
        two_after = str((self.time_source() - 2*self.period) // self.period)

        self.assertFalse(self.otp.compare(two_before, 1))
        self.assertFalse(self.otp.compare(two_after, 1))

if __name__ == '__main__':
    unittest.main()
