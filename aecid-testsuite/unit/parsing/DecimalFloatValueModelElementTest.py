import unittest
import math
from aminer.parsing.MatchContext import MatchContext
from aminer.parsing.DecimalFloatValueModelElement import DecimalFloatValueModelElement
from unit.TestBase import TestBase, DummyMatchContext


class DecimalFloatValueModelElementTest(TestBase):
    """Unittests for the DecimalFloatValueModelElement."""

    def test1get_id(self):
        """Test if get_id works properly."""
        decimal_float_me = DecimalFloatValueModelElement("path",)
        self.assertEqual(decimal_float_me.get_id(), "path")

    def test2get_child_elements(self):
        """Test if get_child_elements returns None."""
        decimal_float_me = DecimalFloatValueModelElement("s0")
        self.assertEqual(decimal_float_me.get_child_elements(), None)

    def test3get_match_element_valid_matches(self):
        """Test valid float values with all possible combinations value_sign_type, value_pad_type and exponent_type."""
        # add test with no decimal .
        # add test with , instead of decimal .

    def test4get_match_element_no_matches(self):
        """Test not matching values with all possible combinations value_sign_type, value_pad_type and exponent_type."""
        # add test with multiple decimal points
        # add test where decimal point is at position 0
        # add test where decimal point is at last position without following decimals

    def test5path_id_input_validation(self):
        """Check if element_id is validated."""
        # empty element_id
        path_id = ""
        self.assertRaises(ValueError, DecimalFloatValueModelElement, path_id)

        # None path_id
        path_id = None
        self.assertRaises(TypeError, DecimalFloatValueModelElement, path_id)

        # bytes element_id is not allowed
        path_id = b"path"
        self.assertRaises(TypeError, DecimalFloatValueModelElement, path_id)

        # integer element_id is not allowed
        path_id = 123
        self.assertRaises(TypeError, DecimalFloatValueModelElement, path_id)

        # float element_id is not allowed
        path_id = 123.22
        self.assertRaises(TypeError, DecimalFloatValueModelElement, path_id)

        # dict element_id is not allowed
        path_id = {"id": "path"}
        self.assertRaises(TypeError, DecimalFloatValueModelElement, path_id)

        # list element_id is not allowed
        path_id = ["path"]
        self.assertRaises(TypeError, DecimalFloatValueModelElement, path_id)

        # empty list element_id is not allowed
        path_id = []
        self.assertRaises(TypeError, DecimalFloatValueModelElement, path_id)

    def test6value_sign_type_input_validation(self):
        """Check if value_sign_type is validated."""
        path_id = "path"
        value_sign_type = "None"
        self.assertRaises(ValueError, DecimalFloatValueModelElement, path_id, value_sign_type=value_sign_type)

        value_sign_type = None
        self.assertRaises(TypeError, DecimalFloatValueModelElement, path_id, value_sign_type=value_sign_type)

        value_sign_type = b"none"
        self.assertRaises(TypeError, DecimalFloatValueModelElement, path_id, value_sign_type=value_sign_type)

        value_sign_type = 123
        self.assertRaises(TypeError, DecimalFloatValueModelElement, path_id, value_sign_type=value_sign_type)

        value_sign_type = 123.22
        self.assertRaises(TypeError, DecimalFloatValueModelElement, path_id, value_sign_type=value_sign_type)

        value_sign_type = {"value_sign_type": "none"}
        self.assertRaises(TypeError, DecimalFloatValueModelElement, path_id, value_sign_type=value_sign_type)

        value_sign_type = ["none"]
        self.assertRaises(TypeError, DecimalFloatValueModelElement, path_id, value_sign_type=value_sign_type)

        value_sign_type = []
        self.assertRaises(TypeError, DecimalFloatValueModelElement, path_id, value_sign_type=value_sign_type)

    def test7value_pad_type_input_validation(self):
        """Check if value_pad_type is validated."""
        # also test if self.pad_characters is set correctly.

    def test8exponent_type_input_validation(self):
        """Check if exponent_type is validated."""





















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
            None, DecimalFloatValueModelElement.SIGN_TYPE_NONE, DecimalFloatValueModelElement.PAD_TYPE_NONE,
            DecimalFloatValueModelElement.EXP_TYPE_NONE)
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
            None, DecimalFloatValueModelElement.SIGN_TYPE_NONE, DecimalFloatValueModelElement.PAD_TYPE_NONE,
            DecimalFloatValueModelElement.EXP_TYPE_NONE)
        match_element = decimal_float_value_me.get_match_element(None, match_context)
        self.assertEqual(match_element, None, self.match_element_should_not_exist)

    def test3negative_number_none_padding(self):
        """
        This testcase represents the equivalence class of negative numbers in combination with no padding.
        It tests the correctness of the path usage for all negative integers without padding.
        """
        match_context = MatchContext(self.negative_string)
        decimal_float_value_me = DecimalFloatValueModelElement(
            None, DecimalFloatValueModelElement.SIGN_TYPE_OPTIONAL, DecimalFloatValueModelElement.PAD_TYPE_NONE,
            DecimalFloatValueModelElement.EXP_TYPE_NONE)
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
            None, DecimalFloatValueModelElement.SIGN_TYPE_NONE, DecimalFloatValueModelElement.PAD_TYPE_NONE,
            DecimalFloatValueModelElement.EXP_TYPE_NONE)
        match_element = decimal_float_value_me.get_match_element(None, match_context)
        self.assertEqual(match_element, None, self.match_element_should_not_exist)

    def test5sign_type_mandatory_none_padding(self):
        """
        This testcase represents the equivalence class of all numbers with a mandatory sign in combination with no padding.
        It tests the correctness of the Path usage for all integers with a mandatory sign without padding.
        """
        match_context = MatchContext(self.negative_string)
        decimal_float_value_me = DecimalFloatValueModelElement(
            None, DecimalFloatValueModelElement.SIGN_TYPE_MANDATORY, DecimalFloatValueModelElement.PAD_TYPE_NONE,
            DecimalFloatValueModelElement.EXP_TYPE_NONE)
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
            None, DecimalFloatValueModelElement.SIGN_TYPE_MANDATORY, DecimalFloatValueModelElement.PAD_TYPE_NONE,
            DecimalFloatValueModelElement.EXP_TYPE_NONE)
        match_element = decimal_float_value_me.get_match_element(None, match_context)
        self.assertEqual(match_element, None, self.match_element_should_not_exist)

    def test7positive_number_zero_padding(self):
        """In this testcase the positive Integer equivalence class in combination with the zero padding is tested."""
        match_context = MatchContext(b'00025537.21 uid=2')
        decimal_float_value_me = DecimalFloatValueModelElement(
            None, DecimalFloatValueModelElement.SIGN_TYPE_NONE, DecimalFloatValueModelElement.PAD_TYPE_ZERO,
            DecimalFloatValueModelElement.EXP_TYPE_NONE)
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
            None, DecimalFloatValueModelElement.SIGN_TYPE_NONE, DecimalFloatValueModelElement.PAD_TYPE_ZERO,
            DecimalFloatValueModelElement.EXP_TYPE_NONE)
        match_element = decimal_float_value_me.get_match_element(None, match_context)
        self.assertEqual(match_element, None, self.match_element_should_not_exist)

    def test9negative_number_blank_padding(self):
        """In this testcase the negative Integer equivalence class in combination with the blank character padding is tested."""
        match_context = MatchContext(b'- 25537.21 uid=2')
        decimal_float_value_me = DecimalFloatValueModelElement(
            None, DecimalFloatValueModelElement.SIGN_TYPE_OPTIONAL, DecimalFloatValueModelElement.PAD_TYPE_BLANK,
            DecimalFloatValueModelElement.EXP_TYPE_NONE)
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
            None, DecimalFloatValueModelElement.SIGN_TYPE_OPTIONAL, DecimalFloatValueModelElement.PAD_TYPE_BLANK,
            DecimalFloatValueModelElement.EXP_TYPE_NONE)
        match_element = decimal_float_value_me.get_match_element(None, match_context)
        self.assertEqual(match_element, None, self.match_element_should_not_exist)

    def test11mandatory_zero_padding(self):
        """In this testcase the mandatory sign equivalence class in combination with the zero padding is tested."""
        match_context = MatchContext(b'+00025537.21 uid=2')
        decimal_float_value_me = DecimalFloatValueModelElement(
            None, DecimalFloatValueModelElement.SIGN_TYPE_MANDATORY, DecimalFloatValueModelElement.PAD_TYPE_ZERO,
            DecimalFloatValueModelElement.EXP_TYPE_NONE)
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
            None, DecimalFloatValueModelElement.SIGN_TYPE_MANDATORY, DecimalFloatValueModelElement.PAD_TYPE_ZERO,
            DecimalFloatValueModelElement.EXP_TYPE_NONE)
        match_element = decimal_float_value_me.get_match_element(None, match_context)
        self.assertEqual(match_element, None, self.match_element_should_not_exist)

        match_context = MatchContext(self.positive_string)
        match_element = decimal_float_value_me.get_match_element(None, match_context)
        self.assertEqual(match_element, None, self.match_element_should_not_exist)

    def test13mandatory_none_padding_exponent(self):
        """In this testcase the mandatory sign equivalence class in combination with the None padding and exponent type mandatory."""
        match_context = MatchContext(b'+25537.21e10 uid=2')
        decimal_float_value_me = DecimalFloatValueModelElement(
            None, DecimalFloatValueModelElement.SIGN_TYPE_MANDATORY, DecimalFloatValueModelElement.PAD_TYPE_NONE,
            DecimalFloatValueModelElement.EXP_TYPE_MANDATORY)
        match_element = decimal_float_value_me.get_match_element(None, match_context)
        self.assertNotEqual(match_element, None, self.match_element_should_exist)
        self.assertEqual(match_element.get_match_string(), b'+25537.21e10', self.match_element_unexpected_result)
        self.assertEqual(match_element.get_match_object(), 25537.21 * math.pow(10, 10), self.match_element_unexpected_value)

        match_context = MatchContext(b'+25537.21e uid=2')
        decimal_float_value_me = DecimalFloatValueModelElement(
            None, DecimalFloatValueModelElement.SIGN_TYPE_MANDATORY, DecimalFloatValueModelElement.PAD_TYPE_NONE,
            DecimalFloatValueModelElement.EXP_TYPE_MANDATORY)
        match_element = decimal_float_value_me.get_match_element(None, match_context)
        self.assertEqual(match_element, None, self.match_element_should_not_exist)


if __name__ == "__main__":
    unittest.main()
