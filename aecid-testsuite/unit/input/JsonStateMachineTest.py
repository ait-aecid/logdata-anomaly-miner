import unittest
from aminer.input.JsonStateMachine import json_machine, constant_machine, string_machine, utf8_machine, hex_machine, number_machine,\
    array_machine, object_machine
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
        """Test boundary values before and after 0-9, a-f, A-F."""
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
        def check_value(_data):  # skipcq: PY-D0003, PTC-W0049
            pass
        string = b"\u02FF"  # skipcq: PYL-W1402
        state = string_machine(check_value)
        hex_machine_found = False
        for c in string:
            state = state(c)
            if state.__name__ == '_hex':
                hex_machine_found = True
        self.assertIsNone(state(ord(b'"')))
        self.assertTrue(hex_machine_found)

        string = b"\uff02"  # skipcq: PYL-W1402
        state = string_machine(check_value)
        hex_machine_found = False
        for c in string:
            state = state(c)
            if state.__name__ == '_hex':
                hex_machine_found = True
        self.assertIsNone(state(ord(b'"')))
        self.assertTrue(hex_machine_found)

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
        def raise_error(_):  # skipcq: PY-D0003
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
        def raise_error(_):  # skipcq: PY-D0003
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
        def raise_error(_):  # skipcq: PY-D0003
            raise Exception("Valid UTF-8 value found in boundary test!")
        self.assertIsNone(utf8_machine(240, raise_error)(127))
        self.assertIsNone(utf8_machine(240, raise_error)(192))
        self.assertIsNone(utf8_machine(240, raise_error)(128)(127))
        self.assertIsNone(utf8_machine(240, raise_error)(191)(192))
        self.assertIsNone(utf8_machine(240, raise_error)(128)(128)(127))
        self.assertIsNone(utf8_machine(240, raise_error)(191)(191)(192))
        self.assertRaises(Exception, utf8_machine(240, raise_error)(128)(128), 128)
        self.assertRaises(Exception, utf8_machine(240, raise_error)(191)(191), 191)

    def test12utf8_machine_started_from_string_machine(self):
        """Test if the utf8_machine is started from the string_machine."""
        def check_value(_data):  # skipcq: PY-D0003, PTC-W0049
            pass
        string = b"File pattern: file\x5f<file-nr>.txt"
        state = string_machine(check_value)
        utf8_machine_found = False
        for c in string:
            state = state(c)
            if state.__name__ == '_utf8':
                utf8_machine_found = True
        self.assertIsNone(state(ord(b'"')))
        self.assertFalse(utf8_machine_found)

        string = b"It is 20\xc2\xb0C"
        state = string_machine(check_value)
        utf8_machine_found = False
        for c in string:
            state = state(c)
            if state.__name__ == '_utf8':
                utf8_machine_found = True
        self.assertIsNone(state(ord(b'"')))
        self.assertTrue(utf8_machine_found)

        string = b"This is a foreign letter: \xe0\xa0\xab"
        state = string_machine(check_value)
        utf8_machine_found = False
        for c in string:
            state = state(c)
            if state.__name__ == '_utf8':
                utf8_machine_found = True
        self.assertIsNone(state(ord(b'"')))
        self.assertTrue(utf8_machine_found)

        string = b"This is an egyptian hieroglyph: \xf0\x93\x80\x90"
        state = string_machine(check_value)
        utf8_machine_found = False
        for c in string:
            state = state(c)
            if state.__name__ == '_utf8':
                utf8_machine_found = True
        self.assertIsNone(state(ord(b'"')))
        self.assertTrue(utf8_machine_found)

    def test13string_machine_valid_values(self):
        """Test the string_machine with all valid characters."""
        def check_value(data):  # skipcq: PY-D0003
            self.assertEqual(data, allowed_chars)
        allowed_chars = ""
        for c in range(0x20, 0x80):
            if c in (0x22, 0x5c):  # skip "\
                continue
            allowed_chars += chr(c)
        state = string_machine(check_value)
        for c in allowed_chars.encode():
            state = state(c)
        self.assertEqual(state.__name__, "_string")
        state = state(ord('"'))
        self.assertIsNone(state)

    def test14string_machine_invalid_values(self):
        """Test the string_machine with some invalid values."""
        def raise_error(_):  # skipcq: PY-D0003
            raise Exception("Invalid returned as valid.")
        for c in range(0x20):  # ascii control characters
            state = string_machine(raise_error)
            self.assertIsNone(state(c))

        for c in range(0x80, 0xc0):  # some characters after the ascii table
            state = string_machine(raise_error)
            self.assertIsNone(state(c))

    def test15string_machine_escaped_strings(self):
        """Test all allowed escape strings in the string_machine."""
        def check_value(data):  # skipcq: PY-D0003
            self.assertEqual(data, compare_strings)
        escape_strings = b"bf\"\\/"
        compare_strings = "\b\f\"\\/"
        state = string_machine(check_value)
        for c in escape_strings:
            state = state(0x5c)  # \
            state = state(c)
        state = state(0x22)  # "
        self.assertIsNone(state)

    def test16constant_machine_valid_values(self):
        """Test all allowed values for the constant_machine. The first letter was already handled by the json_machine."""
        def check_value(data):  # skipcq: PY-D0003
            self.assertEqual(data, value)
        TRUE = [0x72, 0x75, 0x65]
        FALSE = [0x61, 0x6c, 0x73, 0x65]
        NULL = [0x75, 0x6c, 0x6c]
        value = True
        state = constant_machine(TRUE, True, check_value)
        for t in TRUE:
            state = state(t)
        self.assertIsNone(state)

        value = False
        state = constant_machine(FALSE, False, check_value)
        for f in FALSE:
            state = state(f)
        self.assertIsNone(state)

        value = None
        state = constant_machine(NULL, None, check_value)
        for n in NULL:
            state = state(n)
        self.assertIsNone(state)

    def test17constant_machine_invalid_values(self):
        """Test if constant_machine fails. The first letter was already handled by the json_machine."""
        def raise_error(_):  # skipcq: PY-D0003
            raise Exception("Invalid returned as valid.")
        TRUE = [0x72, 0x75, 0x65]
        TRUE_UPPER = [0x52, 0x55, 0x45]
        FALSE = [0x61, 0x6c, 0x73, 0x65]
        FALSE_UPPER = [0x41, 0x4c, 0x53, 0x45]
        NULL = [0x75, 0x6c, 0x6c]
        NULL_UPPER = [0x55, 0x4c, 0x4c]
        NONE = [0x6f, 0x6e, 0x65]
        state = constant_machine(TRUE, True, raise_error)
        self.assertIsNone(state(TRUE_UPPER[0]))

        state = constant_machine(FALSE, False, raise_error)
        self.assertIsNone(state(FALSE_UPPER[0]))

        state = constant_machine(NULL, None, raise_error)
        self.assertIsNone(state(NULL_UPPER[0]))

        state = constant_machine(NULL, None, raise_error)
        self.assertIsNone(state(NONE[0]))

    def test18constant_machine_started_from_json_machine(self):
        """Test if the constant_machine is started from the json_machine. Due to changes in the json_machine all values must be objects."""
        def check_value(data):  # skipcq: PY-D0003
            self.assertEqual(data, {'var': value})
        OBJECT_PREFIX = [0x7b, 0x22, 0x76, 0x61, 0x72, 0x22, 0x3a, 0x20]  # {"var":
        TRUE = [0x74, 0x72, 0x75, 0x65]
        FALSE = [0x66, 0x61, 0x6c, 0x73, 0x65]
        NULL = [0x6e, 0x75, 0x6c, 0x6c]
        value = True
        state = json_machine(check_value)
        for t in OBJECT_PREFIX + TRUE:
            state = state(t)
        self.assertEqual(state(ord('}')).__name__, '_value')

        value = False
        state = json_machine(check_value)
        for f in OBJECT_PREFIX + FALSE:
            state = state(f)
        self.assertEqual(state(ord('}')).__name__, '_value')

        value = None
        state = json_machine(check_value)
        for n in OBJECT_PREFIX + NULL:
            state = state(n)
        self.assertEqual(state(ord('}')).__name__, '_value')

    def check_number_machine(self, check_int_value, value, end_sign):  # skipcq: PY-D0003
        state = number_machine(value[0], check_int_value)
        for c in value[1:]:
            state = state(c)
        self.assertIsNone(state(end_sign))

    def test19numbers_machine_valid_values(self):
        """Test valid values in the numbers_machine."""
        def check_int_value(data, byte_data):  # skipcq: PY-D0003
            self.assertEqual(data, int(value))
            self.assertEqual(end_sign, byte_data)

        def check_float_value(data, byte_data):  # skipcq: PY-D0003
            self.assertEqual(data, float(value))
            self.assertEqual(end_sign, byte_data)
        end_sign = ord(',')
        value = b'222'
        self.check_number_machine(check_int_value, value, end_sign)

        value = b'9223372036854775808'  # maxsize 2^64
        self.check_number_machine(check_int_value, value, end_sign)

        ################ REMOVE THIS AFTER FIX ###############
        # if block in numbers_machine needs to be moved to the end.
        # if byte_data == 0x2d:  # -
        #     sign = -1
        #     return _start
        ######################################################
        value = b'-222'
        self.check_number_machine(check_int_value, value, end_sign)

        value = b'+222'
        self.check_number_machine(check_int_value, value, end_sign)

        value = b'21.50'
        self.check_number_machine(check_float_value, value, end_sign)

        value = b'21.05'
        self.check_number_machine(check_float_value, value, end_sign)

        value = b'-21.05'
        self.check_number_machine(check_float_value, value, end_sign)

        value = b'1.56E-5'
        self.check_number_machine(check_float_value, value, end_sign)

        value = b'1.56e-5'
        self.check_number_machine(check_float_value, value, end_sign)

    def test20numbers_machine_end_signs(self):
        """Check if all non numerical signs end the numbers_machine."""
        def check_int_value(data, byte_data):  # skipcq: PY-D0003
            self.assertEqual(data, int(value))
            self.assertEqual(end_sign, byte_data)
        value = b'222'
        end_signs = list(range(0x2e)) + list(range(0x3a, 0x45)) + list(range(0x46, 0x65)) + list(range(0x66, 0x80))
        valid_signs = [0x2e, 0x45, 0x65] + list(range(0x30, 0x39))
        for end_sign in end_signs:
            state = number_machine(value[0], check_int_value)
            for c in value[1:]:
                state = state(c)
            self.assertIsNone(state(end_sign))
        for end_sign in valid_signs:
            state = number_machine(value[0], check_int_value)
            for c in value[1:]:
                state = state(c)
            self.assertIsNotNone(state(end_sign))

    def test21numbers_machine_invalid_values(self):
        """Test invalid values in the numbers_machine."""
        def raise_error(_data, _byte_data):  # skipcq: PY-D0003
            raise Exception("Invalid number treated as valid!")
        value = b'- 222'
        state = number_machine(value[0], raise_error)
        self.assertIsNone(state(value[1]))

        ################ REMOVE AFTER FIX #########
        # change following code in _start
        # if byte_data == 0x30:
        #     return _mid
        # to
        # if byte_data == 0x30:
        #     return None
        ###########################################
        # octal number
        value = b'0222'
        self.assertIsNone(number_machine(value[0], raise_error))

        # negative octal number
        value = b'-0222'
        state = number_machine(value[0], raise_error)
        self.assertIsNone(state(value[1]))

        # hex number
        value = b'0x80'
        self.assertIsNone(number_machine(value[0], raise_error))

        value = b'NaN'
        self.assertIsNone(number_machine(value[0], raise_error))

        value = b'Infinity'
        self.assertIsNone(number_machine(value[0], raise_error))

        value = b'.1'
        self.assertIsNone(number_machine(value[0], raise_error))

    def check_number_machine_from_json_machine(self, check_int_value, value, end_sign):  # skipcq: PY-D0003
        state = json_machine(check_int_value)
        for c in value:
            state = state(c)
        self.assertEqual(state(end_sign).__name__, '_value')

    def test22numbers_machine_started_from_json_machine(self):
        """Test if the numbers_machine is started from the json_machine."""
        def check_int_value(data):  # skipcq: PY-D0003
            self.assertEqual(data, {'value': int(value)})

        def check_float_value(data):  # skipcq: PY-D0003
            self.assertEqual(data, {'value': float(value)})
        end_sign = ord('}')
        object_prefix = b'{"value": '
        value = b'222'
        self.check_number_machine_from_json_machine(check_int_value, object_prefix+value, end_sign)

        value = b'9223372036854775808'  # maxsize 2^64
        self.check_number_machine_from_json_machine(check_int_value, object_prefix+value, end_sign)

        ################ REMOVE THIS AFTER FIX ###############
        # if block in numbers_machine needs to be moved to the end.
        # if byte_data == 0x2d:  # -
        #     sign = -1
        #     return _start
        ######################################################
        value = b'-222'
        self.check_number_machine_from_json_machine(check_int_value, object_prefix+value, end_sign)

        value = b'+222'
        self.check_number_machine_from_json_machine(check_int_value, object_prefix+value, end_sign)

        value = b'21.50'
        self.check_number_machine_from_json_machine(check_float_value, object_prefix+value, end_sign)

        value = b'21.05'
        self.check_number_machine_from_json_machine(check_float_value, object_prefix+value, end_sign)

        value = b'-21.05'
        self.check_number_machine_from_json_machine(check_float_value, object_prefix+value, end_sign)

        value = b'1.56E-5'
        self.check_number_machine_from_json_machine(check_float_value, object_prefix+value, end_sign)

        value = b'1.56e-5'
        self.check_number_machine_from_json_machine(check_float_value, object_prefix+value, end_sign)

    def test23array_machine_valid_array(self):
        """Test possible valid arrays."""
        def check_value(data):  # skipcq: PY-D0003
            self.assertEqual(data, compare_value)
        value = b'"string", 22, 22.50, true, false, null]'
        compare_value = ['string', 22, 22.5, True, False, None]
        state = array_machine(check_value)
        for c in value:
            state = state(c)
        self.assertIsNone(state)

        value = b'\n\t\t"string",\n\t\t22,\n\t\t22.50,\n\t\ttrue,\n\t\tfalse,\n\t\tnull]'
        state = array_machine(check_value)
        for c in value:
            state = state(c)
        self.assertIsNone(state)

        value = b'{"value": 22}, {"value": "string"}]'
        compare_value = [{'value': 22}, {'value': 'string'}]
        state = array_machine(check_value)
        for c in value:
            state = state(c)
        self.assertIsNone(state)

    def test24array_machine_invalid_formats(self):
        """Test the array_machine with invalid formats."""
        def raise_error(_):  # skipcq: PY-D0003
            raise Exception("Invalid returned as valid.")
        value = b'"string" 22, 22.50, true, false, null]'
        state = array_machine(raise_error)
        for c in value[:value.index(b'2') + 1]:
            state = state(c)
        self.assertIsNone(state)

        value = b'"key": {"value": 2}]'
        state = array_machine(raise_error)
        for c in value[:value.index(b':') + 1]:
            state = state(c)
        self.assertIsNone(state)

    def test25array_machine_started_from_json_machine(self):
        """Test if the array_machine is started from the json_machine."""
        def check_value(data):  # skipcq: PY-D0003
            self.assertEqual(data, compare_value)
        value = b'{"values_array": ["string", 22, 22.50, true, false, null]}'
        compare_value = {'values_array': ['string', 22, 22.5, True, False, None]}
        state = json_machine(check_value)
        for c in value:
            state = state(c)
        self.assertEqual(state.__name__, '_value')

        value = b'{"values_array": [\n\t\t"string",\n\t\t22,\n\t\t22.50,\n\t\ttrue,\n\t\tfalse,\n\t\tnull]}'
        state = json_machine(check_value)
        for c in value:
            state = state(c)
        self.assertEqual(state.__name__, '_value')

        value = b'{"objects_array": [{"value": 22}, {"value": "string"}]}'
        compare_value = {'objects_array': [{'value': 22}, {'value': 'string'}]}
        state = json_machine(check_value)
        for c in value:
            state = state(c)
        self.assertEqual(state.__name__, '_value')

    def test26object_machine_valid_objects(self):
        """Check if the object_machine can handle different valid formats."""
        # single line, no spaces
        value = b'{"string":"Hello World","integer":22,"float":22.23,"bool":true,"array":}'
        # state = object_machine(print)
        # for c in value:
        #     state = state(c)
        # self.assertEqual(state(end_sign).__name__, '_value')
        # single line with spaces
        # multiline with tabs

    def test27object_machine_invalid_values(self):
        """Test the object_machine with invalid values."""
        # keys without "
        # = instead of :
        # no comma after attribute

    def test28object_machine_started_from_json_machine(self):
        """Test if the object_machine is started from the json_machine."""


if __name__ == "__main__":
    unittest.main()
