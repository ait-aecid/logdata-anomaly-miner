import unittest
from aminer.parsing.MatchContext import MatchContext
from aminer.parsing.DecimalIntegerValueModelElement import DecimalIntegerValueModelElement
from aminer.parsing.FirstMatchModelElement import FirstMatchModelElement
from aminer.parsing.FixedDataModelElement import FixedDataModelElement


class FirstDataModelElementTest(unittest.TestCase):
    string = b'25537 uid=2'
    wrong_match_element = 'Wrong MatchElement'

    '''
    This test case proves the intended functionality of single Matches
    '''
    def test1single_match(self):
      self.match_context = MatchContext(self.string)
      self.decimal_integer_value_me = DecimalIntegerValueModelElement(None,
          DecimalIntegerValueModelElement.SIGN_TYPE_NONE, DecimalIntegerValueModelElement.PAD_TYPE_NONE)
      self.fixed_dme = FixedDataModelElement('s0', b'pid=')
      self.first_match_model_element = FirstMatchModelElement('first', [self.decimal_integer_value_me, self.fixed_dme])
      self.assertEqual(self.first_match_model_element.get_match_element('first', self.match_context).get_match_string(),
        b'25537', self.wrong_match_element)
      
      self.match_context = MatchContext(b'pid=')
      self.first_match_model_element = FirstMatchModelElement('first', [self.decimal_integer_value_me, self.fixed_dme])
      self.assertEqual(self.first_match_model_element.get_match_element('first', self.match_context).get_match_string(),
        b'pid=', self.wrong_match_element)
    
    def test2no_match(self):
      self.match_context = MatchContext(b'pid = 25537 uid=2')
      self.decimal_integer_value_me = DecimalIntegerValueModelElement(None,
          DecimalIntegerValueModelElement.SIGN_TYPE_NONE, DecimalIntegerValueModelElement.PAD_TYPE_NONE)
      self.fixed_dme = FixedDataModelElement('s0', b'pid=')
      self.first_match_model_element = FirstMatchModelElement('first', [self.decimal_integer_value_me, self.fixed_dme])
      self.assertEqual(self.first_match_model_element.get_match_element('first', self.match_context),
        None, 'No MatchElement was expected')
    
    def test3double_match(self):
      self.match_context = MatchContext(self.string)
      self.decimal_integer_value_me = DecimalIntegerValueModelElement(None,
          DecimalIntegerValueModelElement.SIGN_TYPE_NONE, DecimalIntegerValueModelElement.PAD_TYPE_NONE)
      self.fixed_dme = FixedDataModelElement('s0', self.string)
      self.first_match_model_element = FirstMatchModelElement('first', [self.decimal_integer_value_me, self.fixed_dme])
      self.assertEqual(self.first_match_model_element.get_match_element('first', self.match_context).get_match_string(),
        b'25537', self.wrong_match_element)
      
      self.match_context = MatchContext(self.string)
      self.first_match_model_element = FirstMatchModelElement('first', [self.fixed_dme, self.decimal_integer_value_me])
      self.assertEqual(self.first_match_model_element.get_match_element('first', self.match_context).get_match_string(),
        self.string, self.wrong_match_element)
    
    def test4child_elements(self):
      self.match_context = MatchContext(self.string)
      self.decimal_integer_value_me = DecimalIntegerValueModelElement(None,
          DecimalIntegerValueModelElement.SIGN_TYPE_NONE, DecimalIntegerValueModelElement.PAD_TYPE_NONE)
      self.fixed_dme = FixedDataModelElement('s0', self.string)
      self.first_match_model_element = FirstMatchModelElement('first', [self.decimal_integer_value_me, self.fixed_dme])
      self.assertEqual(self.first_match_model_element.get_child_elements(), [self.decimal_integer_value_me, self.fixed_dme], 'ChildElements not as expected')
      self.assertRaises(Exception, FirstMatchModelElement('first', []))


if __name__ == "__main__":
    unittest.main()