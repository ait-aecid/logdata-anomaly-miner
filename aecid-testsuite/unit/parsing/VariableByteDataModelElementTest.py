import unittest
from aminer.parsing.MatchContext import MatchContext
from aminer.parsing.VariableByteDataModelElement import VariableByteDataModelElement


class VariableByteDataModelElementTest(unittest.TestCase):
    alphabet = b'abcdefghijklmnopqrstuvwxyz '
    '''
    The matchContext contains only characters of the specified alphabet.
    '''
    def test1match_data_in_alphabet(self):
      match_context = MatchContext(b'this is a normal sentence in lower case.')
      variable_byte_data_model_element = VariableByteDataModelElement('variable', self.alphabet)
      match_element = variable_byte_data_model_element.get_match_element('match', match_context)
      self.assertEqual(match_element.get_match_string(), b'this is a normal sentence in lower case')
      self.assertEqual(match_context.match_data, b'.')
    
    '''
    The matchContext contains characters of the specified alphabet, but does not start with one.
    '''
    def test2match_data_not_starting_with_char_from_alphabet(self):
      match_context = MatchContext(b'.this sentence started with a dot.')
      variable_byte_data_model_element = VariableByteDataModelElement('variable', self.alphabet)
      match_element = variable_byte_data_model_element.get_match_element('match', match_context)
      self.assertEqual(match_element, None)
      self.assertEqual(match_context.match_data, b'.this sentence started with a dot.')
    
    '''
    The matchContext is empty and no matchElement is expected.
    '''
    def test3match_data_empty(self):
      match_context = MatchContext(b'')
      variable_byte_data_model_element = VariableByteDataModelElement('variable', self.alphabet)
      match_element = variable_byte_data_model_element.get_match_element('match', match_context)
      self.assertEqual(match_element, None)
      self.assertEqual(match_context.match_data, b'')


if __name__ == "__main__":
    unittest.main()
