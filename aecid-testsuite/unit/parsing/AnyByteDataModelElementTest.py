import unittest
from aminer.parsing.AnyByteDataModelElement import AnyByteDataModelElement
from aminer.parsing.MatchContext import MatchContext


class AnyByteDataModelElementTest(unittest.TestCase):

    '''
    This test case checks if VALID inputs are accepted.
    '''
    def test1get_match_element_valid_input(self):
      self.match_context = MatchContext(b' some input 123 \}')
      self.any_byte_date_me = AnyByteDataModelElement('id')
      self.assertEqual(self.any_byte_date_me.get_match_element('match1',
        self.match_context).get_match_string(), b' some input 123 \}')
      self.assertEqual(self.any_byte_date_me.get_match_element('match1', self.match_context), None)
      self.match_context = MatchContext(b'1    ')
      self.assertEqual(self.any_byte_date_me.get_match_element('match1',
        self.match_context).get_match_string(), b'1    ')
    
    '''
    This test case checks if INVALID inputs are accepted.
    '''
    def test2get_match_element_invalid_input(self):
      self.match_context = MatchContext(b'')
      self.any_byte_date_me = AnyByteDataModelElement('id')
      self.assertEqual(self.any_byte_date_me.get_match_element('match1',
        self.match_context), None)
      
      self.match_context = MatchContext(None)
      self.assertEqual(self.any_byte_date_me.get_match_element('match1',
        self.match_context), None)


if __name__ == "__main__":
    unittest.main()