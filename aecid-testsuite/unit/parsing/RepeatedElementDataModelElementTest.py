import unittest
from aminer.parsing.MatchContext import MatchContext
from aminer.parsing.FixedDataModelElement import FixedDataModelElement
from aminer.parsing.RepeatedElementDataModelElement import RepeatedElementDataModelElement


class RepeatedElementDataModelElementTest(unittest.TestCase):
    fixed_log_line = b'fixed log line. '

    '''
    This test case verifies the functionality of the repeating Matches.
    '''
    def test1_standard_input_values(self):
      self.match_context = MatchContext(b'fixed log line. \n A different line follows.')
      self.fixed_data_model_element = FixedDataModelElement('fixed', self.fixed_log_line)
      self.repeated_element_data_model_element = RepeatedElementDataModelElement('repeatedElement', self.fixed_data_model_element)
      self.assertEqual(self.repeated_element_data_model_element.get_match_element('match',
        self.match_context).get_match_string(), self.fixed_log_line)
      
      self.match_context = MatchContext(b'fixed log line. fixed log line. fixed log line. fixed log line. \n A different line follows.')
      self.assertEqual(self.repeated_element_data_model_element.get_match_element('match',
        self.match_context).get_match_string(), b'fixed log line. fixed log line. fixed log line. fixed log line. ')
      
      self.match_context = MatchContext(b'A different line follows.')
      self.assertEqual(self.repeated_element_data_model_element.get_match_element('match',
        self.match_context).get_match_string(), b'')

    '''
    This test case verifies the functionality of setting the minimal and maximal repeats.
    '''
    def test2_min_max_repeats(self):
      self.match_context = MatchContext(b'fixed log line. \n A different line follows.')
      self.fixed_data_model_element = FixedDataModelElement('fixed', self.fixed_log_line)
      self.repeated_element_data_model_element = RepeatedElementDataModelElement('repeatedElement',
        self.fixed_data_model_element, 2, 5)
      self.assertEqual(self.repeated_element_data_model_element.get_match_element('match',
        self.match_context), None)
      
      self.match_context = MatchContext(b'fixed log line. fixed log line. \n A different line follows.')
      self.assertEqual(self.repeated_element_data_model_element.get_match_element('match',
        self.match_context).get_match_string(), b'fixed log line. fixed log line. ')
      
      self.match_context = MatchContext(b'fixed log line. fixed log line. fixed log line. fixed log line. fixed log line. \n A different line follows.')
      self.assertEqual(self.repeated_element_data_model_element.get_match_element('match',
        self.match_context).get_match_string(), b'fixed log line. fixed log line. fixed log line. fixed log line. fixed log line. ')
      
      self.match_context = MatchContext(b'fixed log line. fixed log line. fixed log line. fixed log line. fixed log line. fixed log line. \n A different line follows.')
      self.assertEqual(self.repeated_element_data_model_element.get_match_element('match',
        self.match_context), None)


if __name__ == "__main__":
    unittest.main()