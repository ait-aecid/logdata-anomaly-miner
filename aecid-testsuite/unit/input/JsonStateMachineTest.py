import unittest
from aminer.input.JsonStateMachine import json_machine, constant_machine, string_machine, utf8_machine, hex_machine, number_machine,\
    array_machine, object_machine
import sys
from unit.TestBase import TestBase


class ByteStreamLineAtomizerTest(TestBase):
    """Unittests for the JsonStateMachine."""

    def test1hex_machine_valid_values(self):
        """Test the hex_machine with all valid four digit values from 0x0000 to 0xFFFF."""
        def check_value(data):  # skipcq: PY-D0003
            self.assertEqual(data, i)
        for i in range(65536):
            string = str(format(i, '#06x')).encode()[2:]  # remove 0x
            state = hex_machine(check_value)
            for c in string:
                state = state(c)
            self.assertIsNone(state)

        for i in range(65536):
            string = str(format(i, '#06x')).upper().encode()[2:]  # remove 0x
            state = hex_machine(check_value)
            for c in string:
                state = state(c)
            self.assertIsNone(state)

    def test2hex_machine_too_short_value(self):
        """Test the hex_machine with too short hex values."""
        def check_value(data):  # skipcq: PY-D0003
            self.assertEqual(data, i)
        for i in range(4096):
            # converts the integer to the shortest possible hex string.
            string = str(hex(i)).encode()[2:]  # remove 0x
            state = hex_machine(check_value)
            for c in string:
                state = state(c)

        i = 4096
        string = str(hex(i)).encode()[2:]  # remove 0x
        state = hex_machine(check_value)
        for c in string:
            state = state(c)
        self.assertIsNone(state)

    def test3hex_machine_too_long_value(self):
        """Test the hex_machine with too long hex values. All values longer than 4 digits are stripped."""
        def check_value(data):  # skipcq: PY-D0003
            self.assertEqual(data, i)
        # only 00FF is read.
        i = 255
        string = b'0x00FFFF'[2:]  # remove 0x
        state = hex_machine(check_value)
        j = 0
        for j, c in enumerate(string):
            state = state(c)
            if state is None:
                break
        self.assertEqual(j, 3)
        self.assertIsNone(state)

        # only 0F12 is read.
        i = 3858
        string = b'0x0F1234'[2:]  # remove 0x
        state = hex_machine(check_value)
        j = 0
        for j, c in enumerate(string):
            state = state(c)
            if state is None:
                break
        self.assertEqual(j, 3)
        self.assertIsNone(state)

    def test4hex_machine_boundary_values(self):
        """Test boundary values before and after 0-9, a-f, A-F"""
        def check_value(data):  # skipcq: PY-D0003
            self.assertEqual(data, i)
        allowed_value_list = '0123456789abcdefABCDEF'
        forbidden_value_list = [int(hex(j), 16) for j in range(48)] + [int(hex(j), 16) for j in range(58, 65)] + [
            int(hex(j), 16) for j in range(71, 128)]
        for a in allowed_value_list:
            state = hex_machine(check_value)
            string = '0x'+a+a+a+a
            i = int(string, 16)  # convert hex string to integer
            for _ in range(4):
                state = state(ord(a))
            self.assertEqual(state, None)

        for f in forbidden_value_list:
            state = hex_machine(check_value)
            self.assertIsNone(state(f), "value: %d, char: '%s' should not be allowed in the hex_machine!" % (f, chr(f)))

    def test5hex_machine_started_from_string_machine(self):
        """Test if the hex_machine is started from the string_machine."""
        def check_value(_data):  # skipcq: PY-D0003
            pass
        string = b"\u02FF"
        state = string_machine(check_value)
        for c in string:
            state = state(c)
        self.assertIsNone(state(ord(b'"')))

        string = b"\uff02"
        state = string_machine(check_value)
        for c in string:
            state = state(c)
        self.assertIsNone(state(ord(b'"')))

    def test6utf8_machine_allowed_2_byte_values(self):
        """
        Test all allowed values for the utf8_machine with 2 byte values. Only every 4th value is checked to save time.
        This can be changed by changing the step variable. When checking every 4th value the boundary values are also checked.
        """
        def check_value_hex2(data):  # skipcq: PY-D0003
            self.assertEqual(data, (i - 194)*64 + j)
        step = 4
        for i in range(192, 224):
            for j in range(128, 192, step):
                state = utf8_machine(i, check_value_hex2)
                state = state(j)
        # check if the state is None only once to save time.
        self.assertIsNone(state)

    def test7utf8_machine_forbidden_2_byte_boundary_values(self):
        """Test all boundary values for 2 byte utf8 values."""
        def raise_error(_):
            raise Exception("Valid UTF-8 value found in boundary test!")
        self.assertIsNone(utf8_machine(191, raise_error))
        self.assertIsNone(utf8_machine(192, raise_error)(127))
        self.assertIsNone(utf8_machine(192, raise_error)(192))
        self.assertRaises(Exception, utf8_machine(192, raise_error), 128)
        self.assertRaises(Exception, utf8_machine(192, raise_error), 191)

    def test8utf8_machine_allowed_3_byte_values(self):
        """
        Test all allowed values for the utf8_machine with 3 byte values. Only every 4th value is checked to save time.
        This can be changed by changing the step variable. When checking every 4th value the boundary values are also checked.
        """
        def check_value_hex3(data):  # skipcq: PY-D0003
            self.assertEqual(data, (i - 224)*64*64 + (j - 128)*64 + k - 128)
        step = 4
        for i in range(224, 240):
            for j in range(128, 192, step):
                for k in range(128, 192):
                    state = utf8_machine(i, check_value_hex3)
                    state = state(j)
                    state = state(k)
        # check if the state is None only once to save time.
        self.assertIsNone(state)

    def test9utf8_machine_forbidden_3_byte_boundary_values(self):
        """Test all boundary values for 3 byte utf8 values."""
        def raise_error(_):
            raise Exception("Valid UTF-8 value found in boundary test!")
        self.assertIsNone(utf8_machine(224, raise_error)(127))
        self.assertIsNone(utf8_machine(224, raise_error)(192))
        self.assertIsNone(utf8_machine(224, raise_error)(128)(127))
        self.assertIsNone(utf8_machine(224, raise_error)(191)(192))
        self.assertRaises(Exception, utf8_machine(224, raise_error)(128), 128)
        self.assertRaises(Exception, utf8_machine(224, raise_error)(191), 191)

    def test10utf8_machine_allowed_4_byte_values(self):
        """
        Test all allowed values for the utf8_machine with 4 byte values. Only every 4th value is checked to save time.
        This can be changed by changing the step variable. When checking every 4th value the boundary values are also checked.
        """
        def check_value_hex4(data):  # skipcq: PY-D0003
            self.assertEqual(data, (i - 240)*64*64*64 + (j - 128)*64*64 + (k - 128)*64 + m - 128)
        step = 4
        for i in range(240, 248):
            for j in range(128, 192, step):
                for k in range(128, 192, step):
                    for m in range(128, 192, step):
                        state = utf8_machine(i, check_value_hex4)
                        state = state(j)
                        state = state(k)
                        state = state(m)
        # check if the state is None only once to save time.
        self.assertIsNone(state)

    def test11utf8_machine_forbidden_3_byte_boundary_values(self):
        """Test all boundary values for 4 byte utf8 values."""
        def raise_error(_):
            raise Exception("Valid UTF-8 value found in boundary test!")
        self.assertIsNone(utf8_machine(240, raise_error)(127))
        self.assertIsNone(utf8_machine(240, raise_error)(192))
        self.assertIsNone(utf8_machine(240, raise_error)(128)(127))
        self.assertIsNone(utf8_machine(240, raise_error)(191)(192))
        self.assertIsNone(utf8_machine(240, raise_error)(128)(128)(127))
        self.assertIsNone(utf8_machine(240, raise_error)(191)(191)(192))
        self.assertRaises(Exception, utf8_machine(240, raise_error)(128)(128), 128)
        self.assertRaises(Exception, utf8_machine(240, raise_error)(191)(191), 191)


if __name__ == "__main__":
    unittest.main()
