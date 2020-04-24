import unittest
from aminer.parsing.DelimitedDataModelElement import DelimitedDataModelElement
from aminer.parsing.MatchContext import MatchContext


class DelimitedDataModelElementTest(unittest.TestCase):
    match_context_string = b'this is a match context'
    '''
    A single character is used as delimeter.
    '''
    def test1delimeter_single_char(self):
      self.match_context = MatchContext(self.match_context_string)
      self.delimited_data_model_element = DelimitedDataModelElement('id', b'c')
      self.match_element = self.delimited_data_model_element.get_match_element('match', self.match_context)
      self.assertEqual(self.match_element.get_match_string(), b'this is a mat')
      
      self.match_context = MatchContext(self.match_context_string)
      self.delimited_data_model_element = DelimitedDataModelElement('id', b'f')
      self.match_element = self.delimited_data_model_element.get_match_element('match', self.match_context)
      self.assertEqual(self.match_element, None)
      
    '''
    In this test case a whole string is searched for in the matchData.
    '''
    def test2delimeter_string(self):
      self.match_context = MatchContext(self.match_context_string)
      self.delimited_data_model_element = DelimitedDataModelElement('id', b' is')
      self.match_element = self.delimited_data_model_element.get_match_element('match', self.match_context)
      self.assertEqual(self.match_element.get_match_string(), b'this')
    
    '''
    In this test case all not allowed values are tested.
    '''
    def test3delimeter_none_empty_or_not_printable(self):
      self.match_context = MatchContext(self.match_context_string)
      self.delimited_data_model_element = DelimitedDataModelElement('id', b'')
      self.match_element = self.delimited_data_model_element.get_match_element('match', self.match_context)
      self.assertEqual(self.match_element, None)
      
      self.match_context = MatchContext(self.match_context_string)
      self.delimited_data_model_element = DelimitedDataModelElement('id', None)
      self.assertRaises(TypeError, self.delimited_data_model_element.get_match_element, 'match', self.match_context)
      
      self.match_context = MatchContext(self.match_context_string)
      self.delimited_data_model_element = DelimitedDataModelElement('id', b'\x01')
      self.match_element = self.delimited_data_model_element.get_match_element('match', self.match_context)
      self.assertEqual(self.match_element, None)

    '''
    In this test case special character escaping is tested.
    '''
    def test4special_characters_escape(self):
        self.match_context = MatchContext(b'error: the command \\"python run.py\\" was not found" ')
        self.delimited_data_model_element = DelimitedDataModelElement('id', b'"', b'\\')
        self.match_element = self.delimited_data_model_element.get_match_element('match', self.match_context)
        self.assertEqual(self.match_element.get_match_string(), b'error: the command \\"python run.py\\" was not found')

        self.match_context = MatchContext(b'^This is a simple regex string. It costs 10\$.$')
        self.delimited_data_model_element = DelimitedDataModelElement('id', b'$', b'\\')
        self.match_element = self.delimited_data_model_element.get_match_element('match', self.match_context)
        self.assertEqual(self.match_element.get_match_string(), b'^This is a simple regex string. It costs 10\$.')

        self.match_context = MatchContext(b'the searched file is .gitignore.')
        self.delimited_data_model_element = DelimitedDataModelElement('id', b'.', b' ')
        self.match_element = self.delimited_data_model_element.get_match_element('match', self.match_context)
        self.assertEqual(self.match_element.get_match_string(), b'the searched file is .gitignore')


if __name__ == "__main__":
    unittest.main()