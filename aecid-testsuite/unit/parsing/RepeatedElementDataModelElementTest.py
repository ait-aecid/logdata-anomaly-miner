import unittest
from aminer.parsing.MatchContext import MatchContext
from aminer.parsing.FixedDataModelElement import FixedDataModelElement
from aminer.parsing.RepeatedElementDataModelElement import RepeatedElementDataModelElement


class RepeatedElementDataModelElementTest(unittest.TestCase):
    """Unittests for the RepeatedElementDataModelElement."""

    fixed_log_line = b'fixed log line. '

    def test1_standard_input_values(self):
        """This test case verifies the functionality of the repeating Matches."""
        match_context = MatchContext(b'fixed log line. \n A different line follows.')
        fixed_data_model_element = FixedDataModelElement('fixed', self.fixed_log_line)
        repeated_element_data_model_element = RepeatedElementDataModelElement('repeatedElement', fixed_data_model_element)
        self.assertEqual(repeated_element_data_model_element.get_match_element(
            'match', match_context).get_match_string(), self.fixed_log_line)

        match_context = MatchContext(b'fixed log line. fixed log line. fixed log line. fixed log line. \n A different line follows.')
        self.assertEqual(repeated_element_data_model_element.get_match_element(
            'match', match_context).get_match_string(), b'fixed log line. fixed log line. fixed log line. fixed log line. ')

        match_context = MatchContext(b'A different line follows.')
        self.assertEqual(repeated_element_data_model_element.get_match_element('match', match_context), None)

    def test2_min_max_repeats(self):
        """This test case verifies the functionality of setting the minimal and maximal repeats."""
        match_context = MatchContext(b'fixed log line. \n A different line follows.')
        fixed_data_model_element = FixedDataModelElement('fixed', self.fixed_log_line)
        repeated_element_data_model_element = RepeatedElementDataModelElement('repeatedElement', fixed_data_model_element, 2, 5)
        self.assertEqual(repeated_element_data_model_element.get_match_element('match', match_context), None)

        match_context = MatchContext(b'fixed log line. fixed log line. \n A different line follows.')
        self.assertEqual(repeated_element_data_model_element.get_match_element(
            'match', match_context).get_match_string(), b'fixed log line. fixed log line. ')

        match_context = MatchContext(
            b'fixed log line. fixed log line. fixed log line. fixed log line. fixed log line. \n A different line follows.')
        self.assertEqual(repeated_element_data_model_element.get_match_element(
            'match', match_context).get_match_string(), b'fixed log line. fixed log line. fixed log line. fixed log line. fixed log line. ')

        match_context = MatchContext(
            b'fixed log line. fixed log line. fixed log line. fixed log line. fixed log line. fixed log line. \n A different line follows.')
        self.assertEqual(repeated_element_data_model_element.get_match_element('match', match_context), None)


if __name__ == "__main__":
    unittest.main()
