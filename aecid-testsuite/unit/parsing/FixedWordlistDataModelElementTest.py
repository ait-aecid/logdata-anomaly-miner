import unittest
from aminer.parsing.FixedWordlistDataModelElement import FixedWordlistDataModelElement
from aminer.parsing.MatchContext import MatchContext


class FixedWordlistDataModelElementTest(unittest.TestCase):
    """Unittests for the FixedWordlistDataModelElement."""

    def test1sorted_list(self):
        """A valid wordlist is used in this test case."""
        match_context = MatchContext(b'wordlist started with "wordlist"')
        fixed_wordlist_data_model_element = FixedWordlistDataModelElement('wordlist', [b'wordlist', b'word'])
        match_element = fixed_wordlist_data_model_element.get_match_element('match', match_context)
        self.assertEqual(match_element.get_match_string(), b'wordlist')

        match_context = MatchContext(b'words started with "wordlist"')
        fixed_wordlist_data_model_element = FixedWordlistDataModelElement('wordlist', [b'wordlist', b'word'])
        match_element = fixed_wordlist_data_model_element.get_match_element('match', match_context)
        self.assertEqual(match_element.get_match_string(), b'word')

        match_context = MatchContext(b'list started with "wordlist"')
        fixed_wordlist_data_model_element = FixedWordlistDataModelElement('wordlist', [b'wordlist', b'word'])
        match_element = fixed_wordlist_data_model_element.get_match_element('match', match_context)
        self.assertEqual(match_element, None)

    def test2unsorted_list(self):
        """An unsorted wordlist is used in this test case."""
        self.assertRaises(Exception, FixedWordlistDataModelElement, 'wordlist', [b'word', b'wordlist'])


if __name__ == "__main__":
    unittest.main()
