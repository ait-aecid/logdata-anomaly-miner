import unittest
from aminer.parsing.MatchContext import MatchContext
from aminer.parsing.VariableByteDataModelElement import VariableByteDataModelElement


class VariableByteDataModelElementTest(unittest.TestCase):
    """Unittests for the VariableByteDataModelElement."""

    alphabet = b'abcdefghijklmnopqrstuvwxyz '

    def test1match_data_in_alphabet(self):
        """The match_context contains only characters of the specified alphabet."""
        match_context = MatchContext(b'this is a normal sentence in lower case.')
        variable_byte_data_model_element = VariableByteDataModelElement('variable', self.alphabet)
        match_element = variable_byte_data_model_element.get_match_element('match', match_context)
        self.assertEqual(match_element.get_match_string(), b'this is a normal sentence in lower case')
        self.assertEqual(match_context.match_data, b'.')

    def test2match_data_not_starting_with_char_from_alphabet(self):
        """The match_context contains characters of the specified alphabet, but does not start with one."""
        match_context = MatchContext(b'.this sentence started with a dot.')
        variable_byte_data_model_element = VariableByteDataModelElement('variable', self.alphabet)
        match_element = variable_byte_data_model_element.get_match_element('match', match_context)
        self.assertEqual(match_element, None)
        self.assertEqual(match_context.match_data, b'.this sentence started with a dot.')

    def test3match_data_empty(self):
        """No match_element is expected."""
        match_context = MatchContext(b'!')
        variable_byte_data_model_element = VariableByteDataModelElement('variable', self.alphabet)
        match_element = variable_byte_data_model_element.get_match_element('match', match_context)
        self.assertEqual(match_element, None)
        self.assertEqual(match_context.match_data, b'!')


if __name__ == "__main__":
    unittest.main()
