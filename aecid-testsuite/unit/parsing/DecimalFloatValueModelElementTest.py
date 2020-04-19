import unittest
from aminer.parsing.MatchContext import MatchContext
from aminer.parsing.DecimalFloatValueModelElement import DecimalFloatValueModelElement
import math


class DecimalFloatValueModelElementTest(unittest.TestCase):
    positive_string = b'25537.21 uid=2'
    negative_string = b'-25537.21 uid=2'
    negative_number = b'-25537.21'
    match_element_should_exist = 'There should exist a MatchElement!'
    match_element_unexpected_result = 'The MatchElement does not contain the expected result'
    match_element_unexpected_value = 'The MatchElement Value is not as expected'
    match_element_should_not_exist = 'There should not exist a MatchElement!'

    '''
    This testcase represents the equivalence class of positive numbers in combination with no padding.
    It unit the correctness of the Path usage for all positive integers without padding.
    '''
    def test1positive_number_none_padding(self):
      self.match_context = MatchContext(self.positive_string)
      self.decimal_float_value_me = DecimalFloatValueModelElement(None, DecimalFloatValueModelElement.SIGN_TYPE_NONE,
          DecimalFloatValueModelElement.PAD_TYPE_NONE, DecimalFloatValueModelElement.EXP_TYPE_NONE)
      self.match_element = self.decimal_float_value_me.get_match_element(None, self.match_context)
      self.assertNotEqual(self.match_element, None, self.match_element_should_exist)
      self.assertEqual(self.match_element.get_match_string(), b'25537.21', self.match_element_unexpected_result)
      self.assertEqual(self.match_element.get_match_object(), 25537.21, self.match_element_unexpected_value)
    
    '''
    This testcase represents the equivalence class of positive numbers in combination with no padding.
    It unit the correctness of the Path usage for all positive integers without padding, when no match is found.
    '''
    def test2positive_number_none_padding_no_match(self):
      self.match_context = MatchContext(b' 25537.21 uid=2')
      self.decimal_float_value_me = DecimalFloatValueModelElement(None, DecimalFloatValueModelElement.SIGN_TYPE_NONE,
          DecimalFloatValueModelElement.PAD_TYPE_NONE, DecimalFloatValueModelElement.EXP_TYPE_NONE)
      self.match_element = self.decimal_float_value_me.get_match_element(None, self.match_context)
      self.assertEqual(self.match_element, None, self.match_element_should_not_exist)
    
    '''
    This testcase represents the equivalence class of negative numbers in combination with no padding.
    It unit the correctness of the Path usage for all negative integers without padding.
    '''
    def test3negative_number_none_padding(self):
      self.match_context = MatchContext(self.negative_string)
      self.decimal_float_value_me = DecimalFloatValueModelElement(None, DecimalFloatValueModelElement.SIGN_TYPE_OPTIONAL,
          DecimalFloatValueModelElement.PAD_TYPE_NONE, DecimalFloatValueModelElement.EXP_TYPE_NONE)
      self.match_element = self.decimal_float_value_me.get_match_element(None, self.match_context)
      self.assertNotEqual(self.match_element, None, self.match_element_should_exist)
      self.assertEqual(self.match_element.get_match_string(), self.negative_number, self.match_element_unexpected_result)
      self.assertEqual(self.match_element.get_match_object(), -25537.21, self.match_element_unexpected_value)
    
    '''
    This testcase represents the equivalence class of negative numbers in combination with no padding.
    It unit the correctness of the Path usage for all negative integers without padding, when no match is found.
    '''
    def test4negative_number_none_padding_no_match(self):
      self.match_context = MatchContext(b'- 25537.21 uid=2')
      self.decimal_float_value_me = DecimalFloatValueModelElement(None, DecimalFloatValueModelElement.SIGN_TYPE_NONE,
          DecimalFloatValueModelElement.PAD_TYPE_NONE, DecimalFloatValueModelElement.EXP_TYPE_NONE)
      self.match_element = self.decimal_float_value_me.get_match_element(None, self.match_context)
      self.assertEqual(self.match_element, None, self.match_element_should_not_exist)
    
    '''
    This testcase represents the equivalence class of all numbers with a mandatory sign in combination with no padding.
    It unit the correctness of the Path usage for all integers with a mandatory sign without padding.
    '''
    def test5sign_type_mandatory_none_padding(self):
      self.match_context = MatchContext(self.negative_string)
      self.decimal_float_value_me = DecimalFloatValueModelElement(None, DecimalFloatValueModelElement.SIGN_TYPE_MANDATORY,
          DecimalFloatValueModelElement.PAD_TYPE_NONE, DecimalFloatValueModelElement.EXP_TYPE_NONE)
      self.match_element = self.decimal_float_value_me.get_match_element(None, self.match_context)
      self.assertNotEqual(self.match_element, None, self.match_element_should_exist)
      self.assertEqual(self.match_element.get_match_string(), self.negative_number, self.match_element_unexpected_result)
      self.assertEqual(self.match_element.get_match_object(), -25537.21, self.match_element_unexpected_value)
      
      self.match_context = MatchContext(b'+25537 uid=2')
      self.match_element = self.decimal_float_value_me.get_match_element(None, self.match_context)
      self.assertNotEqual(self.match_element, None, self.match_element_should_exist)
      self.assertEqual(self.match_element.get_match_string(), b'+25537', self.match_element_unexpected_result)
      self.assertEqual(self.match_element.get_match_object(), 25537, self.match_element_unexpected_value)
    
    '''
    This testcase represents the equivalence class of all numbers with a mandatory sign in combination with no padding.
    It unit the correctness of the Path usage for all integers with a mandatory sign without padding, when no match is found.
    '''
    def test6sign_type_mandatory_none_padding_no_match(self):
      self.match_context = MatchContext(self.positive_string)
      self.decimal_float_value_me = DecimalFloatValueModelElement(None, DecimalFloatValueModelElement.SIGN_TYPE_MANDATORY,
          DecimalFloatValueModelElement.PAD_TYPE_NONE, DecimalFloatValueModelElement.EXP_TYPE_NONE)
      self.match_element = self.decimal_float_value_me.get_match_element(None, self.match_context)
      self.assertEqual(self.match_element, None, self.match_element_should_not_exist)
      
    '''
    In this testcase the positive Integer equivalence class in combination with the zero padding, which represents
    the padding equivalence class, is tested.
    '''
    def test7positive_number_zero_padding(self):
      self.match_context = MatchContext(b'00025537.21 uid=2')
      self.decimal_float_value_me = DecimalFloatValueModelElement(None, DecimalFloatValueModelElement.SIGN_TYPE_NONE,
          DecimalFloatValueModelElement.PAD_TYPE_ZERO, DecimalFloatValueModelElement.EXP_TYPE_NONE)
      self.match_element = self.decimal_float_value_me.get_match_element(None, self.match_context)
      self.assertNotEqual(self.match_element, None, self.match_element_should_exist)
      self.assertEqual(self.match_element.get_match_string(), b'00025537.21', self.match_element_unexpected_result)
      self.assertEqual(self.match_element.get_match_object(), 25537.21, self.match_element_unexpected_value)
      
      self.match_context = MatchContext(self.positive_string)
      self.match_element = self.decimal_float_value_me.get_match_element(None, self.match_context)
      self.assertNotEqual(self.match_element, None, self.match_element_should_exist)
      self.assertEqual(self.match_element.get_match_string(), b'25537.21', self.match_element_unexpected_result)
      self.assertEqual(self.match_element.get_match_object(), 25537.21, self.match_element_unexpected_value)
    
    '''
    In this testcase the positive Integer equivalence class in combination with the zero padding, which represents
    the padding equivalence class, is tested with no match expected.
    '''
    def test8positive_number_zero_padding_no_match(self):
      self.match_context = MatchContext(b' 00025537.21 uid=2')
      self.decimal_float_value_me = DecimalFloatValueModelElement(None, DecimalFloatValueModelElement.SIGN_TYPE_NONE,
          DecimalFloatValueModelElement.PAD_TYPE_ZERO, DecimalFloatValueModelElement.EXP_TYPE_NONE)
      self.match_element = self.decimal_float_value_me.get_match_element(None, self.match_context)
      self.assertEqual(self.match_element, None, self.match_element_should_not_exist)
    
    '''
    In this testcase the negative Integer equivalence class in combination with the blank character padding, 
    which represents the padding equivalence class, is tested.
    '''
    def test9negative_number_blank_padding(self):
      self.match_context = MatchContext(b'- 25537.21 uid=2')
      self.decimal_float_value_me = DecimalFloatValueModelElement(None, DecimalFloatValueModelElement.SIGN_TYPE_OPTIONAL,
          DecimalFloatValueModelElement.PAD_TYPE_BLANK, DecimalFloatValueModelElement.EXP_TYPE_NONE)
      self.match_element = self.decimal_float_value_me.get_match_element(None, self.match_context)
      self.assertNotEqual(self.match_element, None, self.match_element_should_exist)
      self.assertEqual(self.match_element.get_match_string(), b'- 25537.21', self.match_element_unexpected_result)
      self.assertEqual(self.match_element.get_match_object(), -25537.21, self.match_element_unexpected_value)
      
      self.match_context = MatchContext(self.negative_string)
      self.match_element = self.decimal_float_value_me.get_match_element(None, self.match_context)
      self.assertNotEqual(self.match_element, None, self.match_element_should_exist)
      self.assertEqual(self.match_element.get_match_string(), self.negative_number, self.match_element_unexpected_result)
      self.assertEqual(self.match_element.get_match_object(), -25537.21, self.match_element_unexpected_value)
    
    '''
    In this testcase the negative Integer equivalence class in combination with the blank character padding, 
    which represents the padding equivalence class, is tested with no match expected.
    '''
    def test10negative_number_blank_padding_no_match(self):
      self.match_context = MatchContext(b' -25537 uid=2')
      self.decimal_float_value_me = DecimalFloatValueModelElement(None, DecimalFloatValueModelElement.SIGN_TYPE_OPTIONAL,
          DecimalFloatValueModelElement.PAD_TYPE_BLANK, DecimalFloatValueModelElement.EXP_TYPE_NONE)
      self.match_element = self.decimal_float_value_me.get_match_element(None, self.match_context)
      self.assertEqual(self.match_element, None, self.match_element_should_not_exist)
    
    '''
    In this testcase the mandatory sign equivalence class in combination with the zero padding, 
    which represents the padding equivalence class, is tested.
    '''
    def test11mandatory_zero_padding(self):
      self.match_context = MatchContext(b'+00025537.21 uid=2')
      self.decimal_float_value_me = DecimalFloatValueModelElement(None, DecimalFloatValueModelElement.SIGN_TYPE_MANDATORY,
          DecimalFloatValueModelElement.PAD_TYPE_ZERO, DecimalFloatValueModelElement.EXP_TYPE_NONE)
      self.match_element = self.decimal_float_value_me.get_match_element(None, self.match_context)
      self.assertNotEqual(self.match_element, None, self.match_element_should_exist)
      self.assertEqual(self.match_element.get_match_string(), b'+00025537.21', self.match_element_unexpected_result)
      self.assertEqual(self.match_element.get_match_object(), 25537.21, self.match_element_unexpected_value)
      
      self.match_context = MatchContext(b'-00025537.21 uid=2')
      self.match_element = self.decimal_float_value_me.get_match_element(None, self.match_context)
      self.assertNotEqual(self.match_element, None, self.match_element_should_exist)
      self.assertEqual(self.match_element.get_match_string(), b'-00025537.21', self.match_element_unexpected_result)
      self.assertEqual(self.match_element.get_match_object(), -25537.21, self.match_element_unexpected_value)
      
      self.match_context = MatchContext(b'+25537.21 uid=2')
      self.match_element = self.decimal_float_value_me.get_match_element(None, self.match_context)
      self.assertNotEqual(self.match_element, None, self.match_element_should_exist)
      self.assertEqual(self.match_element.get_match_string(), b'+25537.21', self.match_element_unexpected_result)
      self.assertEqual(self.match_element.get_match_object(), 25537.21, self.match_element_unexpected_value)
    
    '''
    In this testcase the mandatory sign equivalence class in combination with the zero padding, 
    which represents the padding equivalence class, is tested with no match expected.
    '''
    def test12mandatory_zero_padding_no_match(self):
      self.match_context = MatchContext(b'00025537.21 uid=2')
      self.decimal_float_value_me = DecimalFloatValueModelElement(None, DecimalFloatValueModelElement.SIGN_TYPE_MANDATORY,
          DecimalFloatValueModelElement.PAD_TYPE_ZERO, DecimalFloatValueModelElement.EXP_TYPE_NONE)
      self.match_element = self.decimal_float_value_me.get_match_element(None, self.match_context)
      self.assertEqual(self.match_element, None, self.match_element_should_not_exist)
      
      self.match_context = MatchContext(self.positive_string)
      self.match_element = self.decimal_float_value_me.get_match_element(None, self.match_context)
      self.assertEqual(self.match_element, None, self.match_element_should_not_exist)
    
    def test13mandatory_none_padding_exponent(self):
      self.match_context = MatchContext(b'+25537.21e10 uid=2')
      self.decimal_float_value_me = DecimalFloatValueModelElement(None, DecimalFloatValueModelElement.SIGN_TYPE_MANDATORY,
          DecimalFloatValueModelElement.PAD_TYPE_NONE, DecimalFloatValueModelElement.EXP_TYPE_MANDATORY)
      self.match_element = self.decimal_float_value_me.get_match_element(None, self.match_context)
      self.assertNotEqual(self.match_element, None, self.match_element_should_exist)
      self.assertEqual(self.match_element.get_match_string(), b'+25537.21e10', self.match_element_unexpected_result)
      self.assertEqual(self.match_element.get_match_object(), 25537.21 * math.pow(10, 10), self.match_element_unexpected_value)
      
      self.match_context = MatchContext(b'+25537.21e uid=2')
      self.decimal_float_value_me = DecimalFloatValueModelElement(None, DecimalFloatValueModelElement.SIGN_TYPE_MANDATORY,
          DecimalFloatValueModelElement.PAD_TYPE_NONE, DecimalFloatValueModelElement.EXP_TYPE_MANDATORY)
      self.match_element = self.decimal_float_value_me.get_match_element(None, self.match_context)
      self.assertEqual(self.match_element, None, self.match_element_should_not_exist)


if __name__ == "__main__":
    unittest.main()