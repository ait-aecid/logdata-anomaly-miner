import unittest
from aminer.input.JsonStateMachine import json_machine, constant_machine, string_machine, utf8_machine, hex_machine, number_machine,\
    array_machine, object_machine
import sys
from unit.TestBase import TestBase


class ByteStreamLineAtomizerTest(TestBase):
    """Unittests for the JsonStateMachine."""

    def test1hex_machine_valid_values(self):
        """Test the hex_machine with all valid four digit values from 0x0000 to 0xFFFF."""
        def check_value(data):
            self.assertEqual(data, i)
        for i in range(65536):
            string = str(format(i, '#06x')).encode()[2:]  # remove 0x
            state = hex_machine(check_value)
            for c in string:
                state = state(c)
            self.assertIsNone(state)

    def test2hex_machine_too_short_value(self):
        """Test the hex_machine with too short hex values."""
        def check_value(data):
            self.assertEqual(data, i)
        for i in range(4096):
            # converts the integer to the shortest possible hex string.
            string = str(hex(i)).encode()[2:]  # remove 0x
            state = hex_machine(check_value)
            for c in string:
                state = state(c)
            self.assertTrue(isinstance(state, type(hex_machine)))

        i = 4096
        string = str(hex(i)).encode()[2:]  # remove 0x
        state = hex_machine(check_value)
        for c in string:
            state = state(c)
        self.assertIsNone(state)

    def test3hex_machine_too_long_value(self):
        """Test the hex_machine with too long hex values. All values longer than 4 digits are stripped."""
        def check_value(data):
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


if __name__ == "__main__":
    unittest.main()
