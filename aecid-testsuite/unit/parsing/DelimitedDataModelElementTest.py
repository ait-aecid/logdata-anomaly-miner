import unittest
from aminer.parsing.DelimitedDataModelElement import DelimitedDataModelElement
from aminer.parsing.MatchContext import MatchContext


class DelimitedDataModelElementTest(unittest.TestCase):
    """Unittests for the DelimitedDataModelElement."""

    match_context_string = b'this is a match context'

    def test1delimeter_single_char(self):
        """A single character is used as delimeter."""
        match_context = MatchContext(self.match_context_string)
        delimited_data_model_element = DelimitedDataModelElement('id', b'c')
        match_element = delimited_data_model_element.get_match_element('match', match_context)
        self.assertEqual(match_element.get_match_string(), b'this is a mat')

        match_context = MatchContext(self.match_context_string)
        delimited_data_model_element = DelimitedDataModelElement('id', b'f')
        match_element = delimited_data_model_element.get_match_element('match', match_context)
        self.assertEqual(match_element, None)

    def test2delimeter_string(self):
        """In this test case a whole string is searched for in the match_data."""
        match_context = MatchContext(self.match_context_string)
        delimited_data_model_element = DelimitedDataModelElement('id', b' is')
        match_element = delimited_data_model_element.get_match_element('match', match_context)
        self.assertEqual(match_element.get_match_string(), b'this')

    def test3delimeter_none_empty_or_not_printable(self):
        """In this test case all not allowed values are tested."""
        match_context = MatchContext(self.match_context_string)
        delimited_data_model_element = DelimitedDataModelElement('id', b'')
        match_element = delimited_data_model_element.get_match_element('match', match_context)
        self.assertEqual(match_element, None)

        match_context = MatchContext(self.match_context_string)
        delimited_data_model_element = DelimitedDataModelElement('id', None)
        self.assertRaises(TypeError, delimited_data_model_element.get_match_element, 'match', match_context)

        match_context = MatchContext(self.match_context_string)
        delimited_data_model_element = DelimitedDataModelElement('id', b'\x01')
        match_element = delimited_data_model_element.get_match_element('match', match_context)
        self.assertEqual(match_element, None)

    def test4special_characters_escape(self):
        """In this test case special character escaping is tested."""
        match_context = MatchContext(b'error: the command \\"python run.py\\" was not found" ')
        delimited_data_model_element = DelimitedDataModelElement('id', b'"', b'\\')
        match_element = delimited_data_model_element.get_match_element('match', match_context)
        self.assertEqual(match_element.get_match_string(), b'error: the command \\"python run.py\\" was not found')

        match_context = MatchContext(rb'^This is a simple regex string. It costs 10\$.$')
        delimited_data_model_element = DelimitedDataModelElement('id', b'$', b'\\')
        match_element = delimited_data_model_element.get_match_element('match', match_context)
        self.assertEqual(match_element.get_match_string(), rb'^This is a simple regex string. It costs 10\$.')

        match_context = MatchContext(b'the searched file is .gitignore.')
        delimited_data_model_element = DelimitedDataModelElement('id', b'.', b' ')
        match_element = delimited_data_model_element.get_match_element('match', match_context)
        self.assertEqual(match_element.get_match_string(), b'the searched file is .gitignore')


if __name__ == "__main__":
    unittest.main()
