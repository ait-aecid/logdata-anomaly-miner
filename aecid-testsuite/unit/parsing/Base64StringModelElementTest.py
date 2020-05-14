import unittest
from aminer.parsing.Base64StringModelElement import Base64StringModelElement
from aminer.parsing.MatchContext import MatchContext
import base64


class Base64StringModelElementTest(unittest.TestCase):
  base64_string_model_element = Base64StringModelElement('base64')
  match_base64 = 'match/base64'

  '''
  In this test case some legit base64 strings are matched with the ModelElement.
  '''
  def test1_legit_base64_strings(self):
    # string with padding
    string = b'This is some string to be encoded.'
    base64_string = base64.b64encode(string)
    match_context = MatchContext(base64_string)
    match_element = self.base64_string_model_element.get_match_element('match', match_context)
    self.assertEqual(match_element.get_path(), self.match_base64)
    self.assertEqual(match_element.get_match_string(), base64_string)
    self.assertEqual(match_element.get_match_object(), string)
    self.assertEqual(match_element.get_children(), None)
    self.assertEqual(match_context.match_data, b'')
    
    # string without padding
    string = b'This is some string to be encoded without the padding character =.'
    base64_string = base64.b64encode(string)
    match_context = MatchContext(base64_string)
    match_element = self.base64_string_model_element.get_match_element('match', match_context)
    self.assertEqual(match_element.get_path(), self.match_base64)
    self.assertEqual(match_element.get_match_string(), base64_string)
    self.assertEqual(match_element.get_match_object(), string)
    self.assertEqual(match_element.get_children(), None)
    self.assertEqual(match_context.match_data, b'')
  
  '''
  In this test case some base64 strings with not allowed characters are matched with the ModelElement.
  Also the padding checks of base64 strings is tested.
  '''
  def test2_base64_string_with_wrong_characters(self):
    # string with padding
    string = b'This is some string to be encoded.'
    string_after_padding = b'This+string+is+not+encoded+any+more+'
    base64_string = base64.b64encode(string)
    match_context = MatchContext(base64_string+string_after_padding+b'!')
    match_element = self.base64_string_model_element.get_match_element('match', match_context)
    self.assertEqual(match_element.get_path(), self.match_base64)
    self.assertEqual(match_element.get_match_string(), base64_string)
    self.assertEqual(match_element.get_match_object(), string)
    self.assertEqual(match_element.get_children(), None)
    self.assertEqual(match_context.match_data, string_after_padding + b'!')
    
    # string without padding
    string = b'This is some string to be encoded without the padding character =.'
    base64_string = base64.b64encode(string)
    match_context = MatchContext(base64_string+string_after_padding+b'!')
    match_element = self.base64_string_model_element.get_match_element('match', match_context)
    self.assertEqual(match_element.get_path(), self.match_base64)
    self.assertEqual(match_element.get_match_string(), base64_string + string_after_padding)
    self.assertEqual(match_element.get_match_object(), string + base64.b64decode(string_after_padding))
    self.assertEqual(match_element.get_children(), None)
    self.assertEqual(match_context.match_data, b'!')


if __name__ == "__main__":
    unittest.main()
