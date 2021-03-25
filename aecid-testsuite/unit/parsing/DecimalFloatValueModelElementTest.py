import unittest
import math
from aminer.parsing.MatchContext import MatchContext
from aminer.parsing.DecimalFloatValueModelElement import DecimalFloatValueModelElement, SIGN_TYPE_NONE, SIGN_TYPE_OPTIONAL,\
    SIGN_TYPE_MANDATORY, PAD_TYPE_NONE, PAD_TYPE_ZERO, PAD_TYPE_BLANK, EXP_TYPE_NONE, EXP_TYPE_OPTIONAL, EXP_TYPE_MANDATORY
from unit.TestBase import TestBase, DummyMatchContext


class DecimalFloatValueModelElementTest(TestBase):
    """Unittests for the DecimalFloatValueModelElement."""

    #TODO: change checks to use TestBase.compare_result()

    def test1get_id(self):
        """Test if get_id works properly."""
        decimal_float_me = DecimalFloatValueModelElement("path",)
        self.assertEqual(decimal_float_me.get_id(), "path")

    def test2get_child_elements(self):
        """Test if get_child_elements returns None."""
        decimal_float_me = DecimalFloatValueModelElement("s0")
        self.assertEqual(decimal_float_me.get_child_elements(), None)

    def test3get_match_element_default_values(self):
        """Test valid float values with default values of value_sign_type, value_pad_type and exponent_type."""
        decimal_float_value_me = DecimalFloatValueModelElement("path", SIGN_TYPE_NONE, PAD_TYPE_NONE, EXP_TYPE_NONE)
        data = b"22.25"
        match_context = DummyMatchContext(data)
        match_element = decimal_float_value_me.get_match_element("match", match_context)
        self.assertEqual(match_element.match_string, data)
        self.assertEqual(match_element.match_object, 22.25)
        self.assertEqual(match_context.match_string, data)

        data = b"0.25"
        match_context = DummyMatchContext(data)
        match_element = decimal_float_value_me.get_match_element("match", match_context)
        self.assertEqual(match_element.match_string, data)
        self.assertEqual(match_element.match_object, 0.25)
        self.assertEqual(match_context.match_string, data)

        data = b"22"
        match_context = DummyMatchContext(data)
        match_element = decimal_float_value_me.get_match_element("match", match_context)
        self.assertEqual(match_element.match_string, data)
        self.assertEqual(match_element.match_object, 22)
        self.assertEqual(match_context.match_string, data)

        data = b"22.12.2021"
        match_context = DummyMatchContext(data)
        match_element = decimal_float_value_me.get_match_element("match", match_context)
        self.assertEqual(match_element.match_string, b"22.12")
        self.assertEqual(match_element.match_object, 22.12)
        self.assertEqual(match_context.match_string, b"22.12")

        data = b"22. some string"
        match_context = DummyMatchContext(data)
        match_element = decimal_float_value_me.get_match_element("match", match_context)
        self.assertEqual(match_element.match_string, b"22.")
        self.assertEqual(match_element.match_object, 22.0)
        self.assertEqual(match_context.match_string, b"22.")

    def test4get_match_element_default_values(self):
        """Test not matching values with default values of value_sign_type, value_pad_type and exponent_type."""
        decimal_float_value_me = DecimalFloatValueModelElement("path", SIGN_TYPE_NONE, PAD_TYPE_NONE, EXP_TYPE_NONE)
        data = b"+22.25"
        match_context = DummyMatchContext(data)
        self.assertIsNone(decimal_float_value_me.get_match_element("match", match_context))
        self.assertEqual(match_context.match_data, data)

        data = b"-22.25"
        match_context = DummyMatchContext(data)
        self.assertIsNone(decimal_float_value_me.get_match_element("match", match_context))
        self.assertEqual(match_context.match_data, data)

        data = b".25"
        match_context = DummyMatchContext(data)
        self.assertIsNone(decimal_float_value_me.get_match_element("match", match_context))
        self.assertEqual(match_context.match_data, data)
        # add test where decimal point is at last position without following decimals

    def testXelement_id_input_validation(self):
        """Check if element_id is validated."""
        # empty element_id
        element_id = ""
        self.assertRaises(ValueError, DecimalFloatValueModelElement, element_id)

        # None element_id
        element_id = None
        self.assertRaises(TypeError, DecimalFloatValueModelElement, element_id)

        # bytes element_id is not allowed
        element_id = b"path"
        self.assertRaises(TypeError, DecimalFloatValueModelElement, element_id)

        # integer element_id is not allowed
        element_id = 123
        self.assertRaises(TypeError, DecimalFloatValueModelElement, element_id)

        # float element_id is not allowed
        element_id = 123.22
        self.assertRaises(TypeError, DecimalFloatValueModelElement, element_id)

        # dict element_id is not allowed
        element_id = {"id": "path"}
        self.assertRaises(TypeError, DecimalFloatValueModelElement, element_id)

        # list element_id is not allowed
        element_id = ["path"]
        self.assertRaises(TypeError, DecimalFloatValueModelElement, element_id)

        # empty list element_id is not allowed
        element_id = []
        self.assertRaises(TypeError, DecimalFloatValueModelElement, element_id)

    def testXvalue_sign_type_input_validation(self):
        """Check if value_sign_type is validated."""
        element_id = "path"
        DecimalFloatValueModelElement(element_id, value_sign_type="none")
        DecimalFloatValueModelElement(element_id, value_sign_type="optional")
        DecimalFloatValueModelElement(element_id, value_sign_type="mandatory")

        value_sign_type = "None"
        self.assertRaises(ValueError, DecimalFloatValueModelElement, element_id, value_sign_type=value_sign_type)

        value_sign_type = None
        self.assertRaises(TypeError, DecimalFloatValueModelElement, element_id, value_sign_type=value_sign_type)

        value_sign_type = b"none"
        self.assertRaises(TypeError, DecimalFloatValueModelElement, element_id, value_sign_type=value_sign_type)

        value_sign_type = 123
        self.assertRaises(TypeError, DecimalFloatValueModelElement, element_id, value_sign_type=value_sign_type)

        value_sign_type = 123.22
        self.assertRaises(TypeError, DecimalFloatValueModelElement, element_id, value_sign_type=value_sign_type)

        value_sign_type = {"value_sign_type": "none"}
        self.assertRaises(TypeError, DecimalFloatValueModelElement, element_id, value_sign_type=value_sign_type)

        value_sign_type = ["none"]
        self.assertRaises(TypeError, DecimalFloatValueModelElement, element_id, value_sign_type=value_sign_type)

        value_sign_type = []
        self.assertRaises(TypeError, DecimalFloatValueModelElement, element_id, value_sign_type=value_sign_type)

    def testXvalue_pad_type_input_validation(self):
        """Check if value_pad_type is validated."""
        element_id = "path"
        DecimalFloatValueModelElement(element_id, value_pad_type="none")
        DecimalFloatValueModelElement(element_id, value_pad_type="zero")
        DecimalFloatValueModelElement(element_id, value_pad_type="blank")

        value_pad_type = "None"
        self.assertRaises(ValueError, DecimalFloatValueModelElement, element_id, value_pad_type=value_pad_type)

        value_pad_type = None
        self.assertRaises(TypeError, DecimalFloatValueModelElement, element_id, value_pad_type=value_pad_type)

        value_pad_type = b"none"
        self.assertRaises(TypeError, DecimalFloatValueModelElement, element_id, value_pad_type=value_pad_type)

        value_pad_type = 123
        self.assertRaises(TypeError, DecimalFloatValueModelElement, element_id, value_pad_type=value_pad_type)

        value_pad_type = 123.22
        self.assertRaises(TypeError, DecimalFloatValueModelElement, element_id, value_pad_type=value_pad_type)

        value_pad_type = {"value_sign_type": "none"}
        self.assertRaises(TypeError, DecimalFloatValueModelElement, element_id, value_pad_type=value_pad_type)

        value_pad_type = ["none"]
        self.assertRaises(TypeError, DecimalFloatValueModelElement, element_id, value_pad_type=value_pad_type)

        value_pad_type = []
        self.assertRaises(TypeError, DecimalFloatValueModelElement, element_id, value_pad_type=value_pad_type)

    def testXexponent_type_input_validation(self):
        """Check if exponent_type is validated."""
        element_id = "path"
        DecimalFloatValueModelElement(element_id, exponent_type="none")
        DecimalFloatValueModelElement(element_id, exponent_type="optional")
        DecimalFloatValueModelElement(element_id, exponent_type="mandatory")

        exponent_type = "None"
        self.assertRaises(ValueError, DecimalFloatValueModelElement, element_id, exponent_type=exponent_type)

        exponent_type = None
        self.assertRaises(TypeError, DecimalFloatValueModelElement, element_id, exponent_type=exponent_type)

        exponent_type = b"none"
        self.assertRaises(TypeError, DecimalFloatValueModelElement, element_id, exponent_type=exponent_type)

        exponent_type = 123
        self.assertRaises(TypeError, DecimalFloatValueModelElement, element_id, exponent_type=exponent_type)

        exponent_type = 123.22
        self.assertRaises(TypeError, DecimalFloatValueModelElement, element_id, exponent_type=exponent_type)

        exponent_type = {"value_sign_type": "none"}
        self.assertRaises(TypeError, DecimalFloatValueModelElement, element_id, exponent_type=exponent_type)

        exponent_type = ["none"]
        self.assertRaises(TypeError, DecimalFloatValueModelElement, element_id, exponent_type=exponent_type)

        exponent_type = []
        self.assertRaises(TypeError, DecimalFloatValueModelElement, element_id, exponent_type=exponent_type)







    positive_string = b'25537.21 uid=2'
    negative_string = b'-25537.21 uid=2'
    negative_number = b'-25537.21'
    match_element_should_exist = 'There should exist a MatchElement!'
    match_element_unexpected_result = 'The MatchElement does not contain the expected result'
    match_element_unexpected_value = 'The MatchElement Value is not as expected'
    match_element_should_not_exist = 'There should not exist a MatchElement!'

    def test1positive_number_none_padding(self):
        """
        This testcase represents the equivalence class of positive numbers in combination with no padding.
        It tests the correctness of the path usage for all positive integers without padding.
        """
        match_context = MatchContext(self.positive_string)
        decimal_float_value_me = DecimalFloatValueModelElement(
            None, SIGN_TYPE_NONE, PAD_TYPE_NONE,
            EXP_TYPE_NONE)
        match_element = decimal_float_value_me.get_match_element(None, match_context)
        self.assertNotEqual(match_element, None, self.match_element_should_exist)
        self.assertEqual(match_element.get_match_string(), b'25537.21', self.match_element_unexpected_result)
        self.assertEqual(match_element.get_match_object(), 25537.21, self.match_element_unexpected_value)

    def test2positive_number_none_padding_no_match(self):
        """
        This testcase represents the equivalence class of positive numbers in combination with no padding.
        It tests the correctness of the path usage for all positive integers without padding, when no match is found.
        """
        match_context = MatchContext(b' 25537.21 uid=2')
        decimal_float_value_me = DecimalFloatValueModelElement(
            None, SIGN_TYPE_NONE, PAD_TYPE_NONE,
            EXP_TYPE_NONE)
        match_element = decimal_float_value_me.get_match_element(None, match_context)
        self.assertEqual(match_element, None, self.match_element_should_not_exist)

    def test3negative_number_none_padding(self):
        """
        This testcase represents the equivalence class of negative numbers in combination with no padding.
        It tests the correctness of the path usage for all negative integers without padding.
        """
        match_context = MatchContext(self.negative_string)
        decimal_float_value_me = DecimalFloatValueModelElement(
            None, SIGN_TYPE_OPTIONAL, PAD_TYPE_NONE,
            EXP_TYPE_NONE)
        match_element = decimal_float_value_me.get_match_element(None, match_context)
        self.assertNotEqual(match_element, None, self.match_element_should_exist)
        self.assertEqual(match_element.get_match_string(), self.negative_number, self.match_element_unexpected_result)
        self.assertEqual(match_element.get_match_object(), -25537.21, self.match_element_unexpected_value)

    def test4negative_number_none_padding_no_match(self):
        """
        This testcase represents the equivalence class of negative numbers in combination with no padding.
        It tests the correctness of the path usage for all negative integers without padding, when no match is found.
        """
        match_context = MatchContext(b'- 25537.21 uid=2')
        decimal_float_value_me = DecimalFloatValueModelElement(
            None, SIGN_TYPE_NONE, PAD_TYPE_NONE,
            EXP_TYPE_NONE)
        match_element = decimal_float_value_me.get_match_element(None, match_context)
        self.assertEqual(match_element, None, self.match_element_should_not_exist)

    def test5sign_type_mandatory_none_padding(self):
        """
        This testcase represents the equivalence class of all numbers with a mandatory sign in combination with no padding.
        It tests the correctness of the Path usage for all integers with a mandatory sign without padding.
        """
        match_context = MatchContext(self.negative_string)
        decimal_float_value_me = DecimalFloatValueModelElement(
            None, SIGN_TYPE_MANDATORY, PAD_TYPE_NONE,
            EXP_TYPE_NONE)
        match_element = decimal_float_value_me.get_match_element(None, match_context)
        self.assertNotEqual(match_element, None, self.match_element_should_exist)
        self.assertEqual(match_element.get_match_string(), self.negative_number, self.match_element_unexpected_result)
        self.assertEqual(match_element.get_match_object(), -25537.21, self.match_element_unexpected_value)

        match_context = MatchContext(b'+25537 uid=2')
        match_element = decimal_float_value_me.get_match_element(None, match_context)
        self.assertNotEqual(match_element, None, self.match_element_should_exist)
        self.assertEqual(match_element.get_match_string(), b'+25537', self.match_element_unexpected_result)
        self.assertEqual(match_element.get_match_object(), 25537, self.match_element_unexpected_value)

    def test6sign_type_mandatory_none_padding_no_match(self):
        """
        This testcase represents the equivalence class of all numbers with a mandatory sign in combination with no padding.
        It tests the correctness of the Path usage for all integers with a mandatory sign without padding, when no match is found.
        """
        match_context = MatchContext(self.positive_string)
        decimal_float_value_me = DecimalFloatValueModelElement(
            None, SIGN_TYPE_MANDATORY, PAD_TYPE_NONE,
            EXP_TYPE_NONE)
        match_element = decimal_float_value_me.get_match_element(None, match_context)
        self.assertEqual(match_element, None, self.match_element_should_not_exist)

    def test7positive_number_zero_padding(self):
        """In this testcase the positive Integer equivalence class in combination with the zero padding is tested."""
        match_context = MatchContext(b'00025537.21 uid=2')
        decimal_float_value_me = DecimalFloatValueModelElement(
            None, SIGN_TYPE_NONE, PAD_TYPE_ZERO,
            EXP_TYPE_NONE)
        match_element = decimal_float_value_me.get_match_element(None, match_context)
        self.assertNotEqual(match_element, None, self.match_element_should_exist)
        self.assertEqual(match_element.get_match_string(), b'00025537.21', self.match_element_unexpected_result)
        self.assertEqual(match_element.get_match_object(), 25537.21, self.match_element_unexpected_value)

        match_context = MatchContext(self.positive_string)
        match_element = decimal_float_value_me.get_match_element(None, match_context)
        self.assertNotEqual(match_element, None, self.match_element_should_exist)
        self.assertEqual(match_element.get_match_string(), b'25537.21', self.match_element_unexpected_result)
        self.assertEqual(match_element.get_match_object(), 25537.21, self.match_element_unexpected_value)

    def test8positive_number_zero_padding_no_match(self):
        """In this testcase the positive Integer equivalence class in combination with the zero padding is tested with no match expected."""
        match_context = MatchContext(b' 00025537.21 uid=2')
        decimal_float_value_me = DecimalFloatValueModelElement(
            None, SIGN_TYPE_NONE, PAD_TYPE_ZERO,
            EXP_TYPE_NONE)
        match_element = decimal_float_value_me.get_match_element(None, match_context)
        self.assertEqual(match_element, None, self.match_element_should_not_exist)

    def test9negative_number_blank_padding(self):
        """In this testcase the negative Integer equivalence class in combination with the blank character padding is tested."""
        match_context = MatchContext(b'- 25537.21 uid=2')
        decimal_float_value_me = DecimalFloatValueModelElement(
            None, SIGN_TYPE_OPTIONAL, PAD_TYPE_BLANK,
            EXP_TYPE_NONE)
        match_element = decimal_float_value_me.get_match_element(None, match_context)
        self.assertNotEqual(match_element, None, self.match_element_should_exist)
        self.assertEqual(match_element.get_match_string(), b'- 25537.21', self.match_element_unexpected_result)
        self.assertEqual(match_element.get_match_object(), -25537.21, self.match_element_unexpected_value)

        match_context = MatchContext(self.negative_string)
        match_element = decimal_float_value_me.get_match_element(None, match_context)
        self.assertNotEqual(match_element, None, self.match_element_should_exist)
        self.assertEqual(match_element.get_match_string(), self.negative_number, self.match_element_unexpected_result)
        self.assertEqual(match_element.get_match_object(), -25537.21, self.match_element_unexpected_value)

    def test10negative_number_blank_padding_no_match(self):
        """
        In this testcase the negative Integer equivalence class in combination with the blank character padding is tested.
        No match expected.
        """
        match_context = MatchContext(b' -25537 uid=2')
        decimal_float_value_me = DecimalFloatValueModelElement(
            None, SIGN_TYPE_OPTIONAL, PAD_TYPE_BLANK,
            EXP_TYPE_NONE)
        match_element = decimal_float_value_me.get_match_element(None, match_context)
        self.assertEqual(match_element, None, self.match_element_should_not_exist)

    def test11mandatory_zero_padding(self):
        """In this testcase the mandatory sign equivalence class in combination with the zero padding is tested."""
        match_context = MatchContext(b'+00025537.21 uid=2')
        decimal_float_value_me = DecimalFloatValueModelElement(
            None, SIGN_TYPE_MANDATORY, PAD_TYPE_ZERO,
            EXP_TYPE_NONE)
        match_element = decimal_float_value_me.get_match_element(None, match_context)
        self.assertNotEqual(match_element, None, self.match_element_should_exist)
        self.assertEqual(match_element.get_match_string(), b'+00025537.21', self.match_element_unexpected_result)
        self.assertEqual(match_element.get_match_object(), 25537.21, self.match_element_unexpected_value)

        match_context = MatchContext(b'-00025537.21 uid=2')
        match_element = decimal_float_value_me.get_match_element(None, match_context)
        self.assertNotEqual(match_element, None, self.match_element_should_exist)
        self.assertEqual(match_element.get_match_string(), b'-00025537.21', self.match_element_unexpected_result)
        self.assertEqual(match_element.get_match_object(), -25537.21, self.match_element_unexpected_value)

        match_context = MatchContext(b'+25537.21 uid=2')
        match_element = decimal_float_value_me.get_match_element(None, match_context)
        self.assertNotEqual(match_element, None, self.match_element_should_exist)
        self.assertEqual(match_element.get_match_string(), b'+25537.21', self.match_element_unexpected_result)
        self.assertEqual(match_element.get_match_object(), 25537.21, self.match_element_unexpected_value)

    def test12mandatory_zero_padding_no_match(self):
        """In this testcase the mandatory sign equivalence class in combination with the zero padding is tested with no match expected."""
        match_context = MatchContext(b'00025537.21 uid=2')
        decimal_float_value_me = DecimalFloatValueModelElement(
            None, SIGN_TYPE_MANDATORY, PAD_TYPE_ZERO,
            EXP_TYPE_NONE)
        match_element = decimal_float_value_me.get_match_element(None, match_context)
        self.assertEqual(match_element, None, self.match_element_should_not_exist)

        match_context = MatchContext(self.positive_string)
        match_element = decimal_float_value_me.get_match_element(None, match_context)
        self.assertEqual(match_element, None, self.match_element_should_not_exist)

    def test13mandatory_none_padding_exponent(self):
        """In this testcase the mandatory sign equivalence class in combination with the None padding and exponent type mandatory."""
        match_context = MatchContext(b'+25537.21e10 uid=2')
        decimal_float_value_me = DecimalFloatValueModelElement(
            None, SIGN_TYPE_MANDATORY, PAD_TYPE_NONE,
            EXP_TYPE_MANDATORY)
        match_element = decimal_float_value_me.get_match_element(None, match_context)
        self.assertNotEqual(match_element, None, self.match_element_should_exist)
        self.assertEqual(match_element.get_match_string(), b'+25537.21e10', self.match_element_unexpected_result)
        self.assertEqual(match_element.get_match_object(), 25537.21 * math.pow(10, 10), self.match_element_unexpected_value)

        match_context = MatchContext(b'+25537.21e uid=2')
        decimal_float_value_me = DecimalFloatValueModelElement(
            None, SIGN_TYPE_MANDATORY, PAD_TYPE_NONE,
            EXP_TYPE_MANDATORY)
        match_element = decimal_float_value_me.get_match_element(None, match_context)
        self.assertEqual(match_element, None, self.match_element_should_not_exist)


if __name__ == "__main__":
    unittest.main()
