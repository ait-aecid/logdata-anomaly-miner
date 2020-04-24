import unittest
from aminer.parsing.ParserMatch import ParserMatch
from aminer.parsing.MatchElement import MatchElement


class ParserMatchTest(unittest.TestCase):

    '''
    This test case checks if all elements are found in the dictionary.
    '''
    def test1get_match_dictionary(self):
      self.a3 = MatchElement('a3', b'a3', b'a3', [])
      self.a2 = MatchElement('a2', b'a2', b'a2', [self.a3])
      self.a1 = MatchElement('a1', b'a1', b'a1', [self.a2])
      self.b3 = MatchElement('b3', b'b3', b'b3', [])
      self.b2 = MatchElement('b2', b'b2', b'b2', [self.b3])
      self.b1 = MatchElement('b1', b'b1', b'b1', [self.b2])
      
      self.root_element = MatchElement('root', b'root', b'root', [self.a1, self.b1])
      
      self.parser_match = ParserMatch(self.root_element, None)
      self.dict = self.parser_match.get_match_dictionary()
      
      self.assertEqual(self.dict['root'], self.root_element)
      self.assertEqual(self.dict['a1'], self.a1)
      self.assertEqual(self.dict['a2'], self.a2)
      self.assertEqual(self.dict['a3'], self.a3)
      self.assertEqual(self.dict['b1'], self.b1)
      self.assertEqual(self.dict['b2'], self.b2)
      self.assertEqual(self.dict['b3'], self.b3)
    
    '''
    This test case checks if an Exception is thrown, when a wrong type is used.
    '''
    def test2get_match_dictionary_with_match_element_none(self):
      self.a3 = MatchElement('a3', b'a3', b'a3', [None])
      self.a2 = MatchElement('a2', b'a2', b'a2', [self.a3])
      self.a1 = MatchElement('a1', b'a1', b'a1', [self.a2])
      self.b3 = MatchElement('b3', b'b3', b'b3', [None])
      self.b2 = MatchElement('b2', b'b2', b'b2', [self.b3])
      self.b1 = MatchElement('b1', b'b1', b'b1', [self.b2])
      
      self.root_element = MatchElement('root', b'root', b'root', [self.a1, self.b1])
      
      self.parser_match = ParserMatch(self.root_element, None)
      self.assertRaises(AttributeError, self.parser_match.get_match_dictionary)


if __name__ == "__main__":
    unittest.main()