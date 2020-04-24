import unittest
from aminer.parsing.FixedWordlistDataModelElement import FixedWordlistDataModelElement
from aminer.parsing.MatchContext import MatchContext


class FixedWordlistDataModelElementTest(unittest.TestCase):

    '''
    A valid wordlist is used in this test case. 
    '''
    def test1sorted_list(self):
      self.match_context = MatchContext(b'wordlist started with "wordlist"')
      self.fixed_wordlist_data_model_element = FixedWordlistDataModelElement('wordlist', [b'wordlist', b'word'])
      self.match_element = self.fixed_wordlist_data_model_element.get_match_element('match', self.match_context)
      self.assertEqual(self.match_element.get_match_string(), b'wordlist')
      
      self.match_context = MatchContext(b'words started with "wordlist"')
      self.fixed_wordlist_data_model_element = FixedWordlistDataModelElement('wordlist', [b'wordlist', b'word'])
      self.match_element = self.fixed_wordlist_data_model_element.get_match_element('match', self.match_context)
      self.assertEqual(self.match_element.get_match_string(), b'word')
      
      self.match_context = MatchContext(b'list started with "wordlist"')
      self.fixed_wordlist_data_model_element = FixedWordlistDataModelElement('wordlist', [b'wordlist', b'word'])
      self.match_element = self.fixed_wordlist_data_model_element.get_match_element('match', self.match_context)
      self.assertEqual(self.match_element, None)
    
    '''
    An unsorted Wordlist is used in this test case.
    '''
    def test2unsorted_list(self):
      self.assertRaises(Exception, FixedWordlistDataModelElement, 'wordlist', [b'word', b'wordlist'])


if __name__ == "__main__":
    unittest.main()