import unittest
from aminer.parsing.MatchContext import MatchContext
from aminer.parsing.FixedDataModelElement import FixedDataModelElement
from aminer.parsing.OptionalMatchModelElement import OptionalMatchModelElement


class OptionalMatchModelElementTest(unittest.TestCase):

    '''
    Because of the simplicity of the FixedDataModelElement it is used to test possible outcomes of this class.
    '''
    def test1_match_element_expected(self):
      self.match_context = MatchContext(b'This is some String.')
      self.fixed_data_model_element = FixedDataModelElement('fixed', b'This')
      self.optional_match_model_element = OptionalMatchModelElement('optional', self.fixed_data_model_element)
      self.assertEqual(self.optional_match_model_element.get_match_element('match',
        self.match_context).get_match_string(), b'This')
      self.assertEqual(self.match_context.match_data, b' is some String.')
    
    '''
    An Empty MatchElement is expected, due to not finding the fixed String.
    The MatchContext must not be changed.
    '''
    def test2_match_element_empty(self):
      self.match_context = MatchContext(b'Another String.')
      self.fixed_data_model_element = FixedDataModelElement('fixed', b'This')
      self.optional_match_model_element = OptionalMatchModelElement('optional', self.fixed_data_model_element)
      self.assertEqual(self.optional_match_model_element.get_match_element('match',
        self.match_context).get_match_string(), '')
      self.assertEqual(self.match_context.match_data, b'Another String.')


if __name__ == "__main__":
    unittest.main()