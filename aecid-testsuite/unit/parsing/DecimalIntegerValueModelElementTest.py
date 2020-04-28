import unittest
from aminer.parsing.MatchContext import MatchContext
from aminer.parsing.DecimalIntegerValueModelElement import DecimalIntegerValueModelElement


class DecimalIntegerValueModelElementTest(unittest.TestCase):
    positive_string = b'25537 uid=2'
    negative_string = b'-25537 uid=2'
    zero_number = b'00025537 uid=2'
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
      self.decimal_integer_value_me = DecimalIntegerValueModelElement(None,
          DecimalIntegerValueModelElement.SIGN_TYPE_NONE, DecimalIntegerValueModelElement.PAD_TYPE_NONE)
      self.match_element = self.decimal_integer_value_me.get_match_element(None, self.match_context)
      self.assertNotEqual(self.match_element, None, self.match_element_should_exist)
      self.assertEqual(self.match_element.get_match_string(), b'25537', self.match_element_unexpected_result)
      self.assertEqual(self.match_element.get_match_object(), 25537, self.match_element_unexpected_value)
    
    '''
    This testcase represents the equivalence class of positive numbers in combination with no padding.
    It unit the correctness of the Path usage for all positive integers without padding, when no match is found.
    '''
    def test2positive_number_none_padding_no_match(self):
      self.match_context = MatchContext(b' 25537 uid=2')
      self.decimal_integer_value_me = DecimalIntegerValueModelElement(None,
          DecimalIntegerValueModelElement.SIGN_TYPE_NONE, DecimalIntegerValueModelElement.PAD_TYPE_NONE)
      self.match_element = self.decimal_integer_value_me.get_match_element(None, self.match_context)
      self.assertEqual(self.match_element, None, self.match_element_should_not_exist)
    
    '''
    This testcase represents the equivalence class of negative numbers in combination with no padding.
    It unit the correctness of the Path usage for all negative integers without padding.
    '''
    def test3negative_number_none_padding(self):
      self.match_context = MatchContext(self.negative_string)
      self.decimal_integer_value_me = DecimalIntegerValueModelElement(None,
          DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL, DecimalIntegerValueModelElement.PAD_TYPE_NONE)
      self.match_element = self.decimal_integer_value_me.get_match_element(None, self.match_context)
      self.assertNotEqual(self.match_element, None, self.match_element_should_exist)
      self.assertEqual(self.match_element.get_match_string(), b'-25537', self.match_element_unexpected_result)
      self.assertEqual(self.match_element.get_match_object(), -25537, self.match_element_unexpected_value)
    
    '''
    This testcase represents the equivalence class of negative numbers in combination with no padding.
    It unit the correctness of the Path usage for all negative integers without padding, when no match is found.
    '''
    def test4negative_number_none_padding_no_match(self):
      self.match_context = MatchContext(b'- 25537 uid=2')
      self.decimal_integer_value_me = DecimalIntegerValueModelElement(None,
          DecimalIntegerValueModelElement.SIGN_TYPE_NONE, DecimalIntegerValueModelElement.PAD_TYPE_NONE)
      self.match_element = self.decimal_integer_value_me.get_match_element(None, self.match_context)
      self.assertEqual(self.match_element, None, self.match_element_should_not_exist)
    
    '''
    This testcase represents the equivalence class of all numbers with a mandatory sign in combination with no padding.
    It unit the correctness of the Path usage for all integers with a mandatory sign without padding.
    '''
    def test5sign_type_mandatory_none_padding(self):
      self.match_context = MatchContext(self.negative_string)
      self.decimal_integer_value_me = DecimalIntegerValueModelElement(None,
          DecimalIntegerValueModelElement.SIGN_TYPE_MANDATORY, DecimalIntegerValueModelElement.PAD_TYPE_NONE)
      self.match_element = self.decimal_integer_value_me.get_match_element(None, self.match_context)
      self.assertNotEqual(self.match_element, None, self.match_element_should_exist)
      self.assertEqual(self.match_element.get_match_string(), b'-25537', self.match_element_unexpected_result)
      self.assertEqual(self.match_element.get_match_object(), -25537, self.match_element_unexpected_value)
      
      self.match_context = MatchContext(b'+25537 uid=2')
      self.match_element = self.decimal_integer_value_me.get_match_element(None, self.match_context)
      self.assertNotEqual(self.match_element, None, self.match_element_should_exist)
      self.assertEqual(self.match_element.get_match_string(), b'+25537', self.match_element_unexpected_result)
      self.assertEqual(self.match_element.get_match_object(), 25537, self.match_element_unexpected_value)
    
    '''
    This testcase represents the equivalence class of all numbers with a mandatory sign in combination with no padding.
    It unit the correctness of the Path usage for all integers with a mandatory sign without padding, when no match is found.
    '''
    def test6sign_type_mandatory_none_padding_no_match(self):
      self.match_context = MatchContext(self.positive_string)
      self.decimal_integer_value_me = DecimalIntegerValueModelElement(None,
          DecimalIntegerValueModelElement.SIGN_TYPE_MANDATORY, DecimalIntegerValueModelElement.PAD_TYPE_NONE)
      self.match_element = self.decimal_integer_value_me.get_match_element(None, self.match_context)
      self.assertEqual(self.match_element, None, self.match_element_should_not_exist)
      
    '''
    In this testcase the positive Integer equivalence class in combination with the zero padding, which represents
    the padding equivalence class, is tested.
    '''
    def test7positive_number_zero_padding(self):
      self.match_context = MatchContext(self.zero_number)
      self.decimal_integer_value_me = DecimalIntegerValueModelElement(None,
          DecimalIntegerValueModelElement.SIGN_TYPE_NONE, DecimalIntegerValueModelElement.PAD_TYPE_ZERO)
      self.match_element = self.decimal_integer_value_me.get_match_element(None, self.match_context)
      self.assertNotEqual(self.match_element, None, self.match_element_should_exist)
      self.assertEqual(self.match_element.get_match_string(), b'00025537', self.match_element_unexpected_result)
      self.assertEqual(self.match_element.get_match_object(), 25537, self.match_element_unexpected_value)
      
      self.match_context = MatchContext(self.positive_string)
      self.match_element = self.decimal_integer_value_me.get_match_element(None, self.match_context)
      self.assertNotEqual(self.match_element, None, self.match_element_should_exist)
      self.assertEqual(self.match_element.get_match_string(), b'25537', self.match_element_unexpected_result)
      self.assertEqual(self.match_element.get_match_object(), 25537, self.match_element_unexpected_value)
    
    '''
    In this testcase the positive Integer equivalence class in combination with the zero padding, which represents
    the padding equivalence class, is tested with no match expected.
    '''
    def test8positive_number_zero_padding_no_match(self):
      self.match_context = MatchContext(b' 00025537 uid=2')
      self.decimal_integer_value_me = DecimalIntegerValueModelElement(None,
          DecimalIntegerValueModelElement.SIGN_TYPE_NONE, DecimalIntegerValueModelElement.PAD_TYPE_ZERO)
      self.match_element = self.decimal_integer_value_me.get_match_element(None, self.match_context)
      self.assertEqual(self.match_element, None, self.match_element_should_not_exist)
    
    '''
    In this testcase the negative Integer equivalence class in combination with the blank character padding, 
    which represents the padding equivalence class, is tested.
    '''
    def test9negative_number_blank_padding(self):
      self.match_context = MatchContext(b'- 25537 uid=2')
      self.decimal_integer_value_me = DecimalIntegerValueModelElement(None,
          DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL, DecimalIntegerValueModelElement.PAD_TYPE_BLANK)
      self.match_element = self.decimal_integer_value_me.get_match_element(None, self.match_context)
      self.assertNotEqual(self.match_element, None, self.match_element_should_exist)
      self.assertEqual(self.match_element.get_match_string(), b'- 25537', self.match_element_unexpected_result)
      self.assertEqual(self.match_element.get_match_object(), -25537, self.match_element_unexpected_value)
      
      self.match_context = MatchContext(self.negative_string)
      self.match_element = self.decimal_integer_value_me.get_match_element(None, self.match_context)
      self.assertNotEqual(self.match_element, None, self.match_element_should_exist)
      self.assertEqual(self.match_element.get_match_string(), b'-25537', self.match_element_unexpected_result)
      self.assertEqual(self.match_element.get_match_object(), -25537, self.match_element_unexpected_value)
    
    '''
    In this testcase the negative Integer equivalence class in combination with the blank character padding, 
    which represents the padding equivalence class, is tested with no match expected.
    '''
    def test10negative_number_blank_padding_no_match(self):
      self.match_context = MatchContext(b' -25537 uid=2')
      self.decimal_integer_value_me = DecimalIntegerValueModelElement(None,
          DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL, DecimalIntegerValueModelElement.PAD_TYPE_BLANK)
      self.match_element = self.decimal_integer_value_me.get_match_element(None, self.match_context)
      self.assertEqual(self.match_element, None, self.match_element_should_not_exist)
    
    '''
    In this testcase the mandatory sign equivalence class in combination with the zero padding, 
    which represents the padding equivalence class, is tested.
    '''
    def test11mandatory_zero_padding(self):
      self.match_context = MatchContext(b'+00025537 uid=2')
      self.decimal_integer_value_me = DecimalIntegerValueModelElement(None,
          DecimalIntegerValueModelElement.SIGN_TYPE_MANDATORY, DecimalIntegerValueModelElement.PAD_TYPE_ZERO)
      self.match_element = self.decimal_integer_value_me.get_match_element(None, self.match_context)
      self.assertNotEqual(self.match_element, None, self.match_element_should_exist)
      self.assertEqual(self.match_element.get_match_string(), b'+00025537', self.match_element_unexpected_result)
      self.assertEqual(self.match_element.get_match_object(), 25537, self.match_element_unexpected_value)
      
      self.match_context = MatchContext(b'-00025537 uid=2')
      self.match_element = self.decimal_integer_value_me.get_match_element(None, self.match_context)
      self.assertNotEqual(self.match_element, None, self.match_element_should_exist)
      self.assertEqual(self.match_element.get_match_string(), b'-00025537', self.match_element_unexpected_result)
      self.assertEqual(self.match_element.get_match_object(), -25537, self.match_element_unexpected_value)
      
      self.match_context = MatchContext(b'+25537 uid=2')
      self.match_element = self.decimal_integer_value_me.get_match_element(None, self.match_context)
      self.assertNotEqual(self.match_element, None, self.match_element_should_exist)
      self.assertEqual(self.match_element.get_match_string(), b'+25537', self.match_element_unexpected_result)
      self.assertEqual(self.match_element.get_match_object(), 25537, self.match_element_unexpected_value)
    
    '''
    In this testcase the mandatory sign equivalence class in combination with the zero padding, 
    which represents the padding equivalence class, is tested with no match expected.
    '''
    def test12mandatory_zero_padding_no_match(self):
      self.match_context = MatchContext(self.zero_number)
      self.decimal_integer_value_me = DecimalIntegerValueModelElement(None,
          DecimalIntegerValueModelElement.SIGN_TYPE_MANDATORY, DecimalIntegerValueModelElement.PAD_TYPE_ZERO)
      self.match_element = self.decimal_integer_value_me.get_match_element(None, self.match_context)
      self.assertEqual(self.match_element, None, self.match_element_should_not_exist)
      
      self.match_context = MatchContext(self.positive_string)
      self.match_element = self.decimal_integer_value_me.get_match_element(None, self.match_context)
      self.assertEqual(self.match_element, None, self.match_element_should_not_exist)
    
    '''
    This test checks whether the input is validated against the datatype. 
    '''
    def test13_no_number_input(self):
      self.match_context = MatchContext(b'This is no number')
      self.decimal_integer_value_me = DecimalIntegerValueModelElement(None,
          DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL, DecimalIntegerValueModelElement.PAD_TYPE_NONE)
      self.match_element = self.decimal_integer_value_me.get_match_element(None, self.match_context)
      self.assertEqual(self.match_element, None, self.match_element_should_not_exist)
    
    '''
    If the input is valid, but only padding characters can be found, the result should be no match.
    '''
    def test14_valid_padding_no_match(self):
      self.match_context = MatchContext(b'    ')
      self.decimal_integer_value_me = DecimalIntegerValueModelElement(None,
          DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL, DecimalIntegerValueModelElement.PAD_TYPE_BLANK)
      self.match_element = self.decimal_integer_value_me.get_match_element(None, self.match_context)
      self.assertEqual(self.match_element, None, self.match_element_should_not_exist)
      
      self.match_context = MatchContext(b'00000')
      self.decimal_integer_value_me = DecimalIntegerValueModelElement(None,
          DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL, DecimalIntegerValueModelElement.PAD_TYPE_ZERO)
      self.match_element = self.decimal_integer_value_me.get_match_element(None, self.match_context)
      self.assertEqual(self.match_element, None, self.match_element_should_not_exist)
    
    '''
    An exception must be raised, when the sign type is not valid.
    '''
    def test15_invalid_sign_type(self):
      self.match_context = MatchContext(self.zero_number)
      self.assertRaises(Exception, DecimalIntegerValueModelElement, None, 
          'other sign type', DecimalIntegerValueModelElement.PAD_TYPE_ZERO)
    
    '''
    An exception must be raised, when the padding type does not exist.
    '''
    def test16_invalid_padding_type(self):
      self.match_context = MatchContext(self.zero_number)
      self.assertRaises(Exception, DecimalIntegerValueModelElement, None, 
          DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL, 'tab')
    
    '''
    An exception must be raised, when the input is no bytestring. Another possiblity is to convert the string into
    a bytestring.
    '''
    '''
    def test17NoBytestringInput(self):
      self.assertRaises(Exception, MatchContext, '00025537 uid=2')
    '''


if __name__ == "__main__":
    unittest.main()