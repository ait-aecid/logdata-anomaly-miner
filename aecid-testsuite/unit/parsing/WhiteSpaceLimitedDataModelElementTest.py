import unittest
from aminer.parsing.WhiteSpaceLimitedDataModelElement import WhiteSpaceLimitedDataModelElement
from aminer.parsing.MatchContext import MatchContext


class WhiteSpaceLimitedDataModelElementTest(unittest.TestCase):
    """Unittests for the WhiteSpaceLimitedDataModelElement."""

    white_space_limited_data_model_element = WhiteSpaceLimitedDataModelElement('Whitespace String')

    def test1_sentence_with_multiple_whitespaces(self):
        """In this test case a MatchElement is created from a sentence with multiple whitespaces in it."""
        string = b'This is a string with whitespaces.'
        match_context = MatchContext(string)
        match_element = self.white_space_limited_data_model_element.get_match_element('match', match_context)
        self.assertEqual(match_element.get_path(), 'match/Whitespace String')
        self.assertEqual(match_element.get_match_string(), b'This')
        self.assertEqual(match_element.get_match_object(), b'This')
        self.assertEqual(match_element.get_children(), None)
        self.assertEqual(match_context.match_data, b' is a string with whitespaces.')

    def test2_sentence_with_no_whitespaces(self):
        """In this test case a MatchElement is created from a sentence no whitespaces in it."""
        string = b'This+is+a+string+without+any+whitespaces.'
        match_context = MatchContext(string)
        match_element = self.white_space_limited_data_model_element.get_match_element('match', match_context)
        self.assertEqual(match_element.get_path(), 'match/Whitespace String')
        self.assertEqual(match_element.get_match_string(), string)
        self.assertEqual(match_element.get_match_object(), string)
        self.assertEqual(match_element.get_children(), None)
        self.assertEqual(match_context.match_data, b'')


if __name__ == "__main__":
    unittest.main()
