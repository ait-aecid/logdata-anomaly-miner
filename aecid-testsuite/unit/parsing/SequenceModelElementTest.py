import unittest
from aminer.parsing.MatchContext import MatchContext
from aminer.parsing.FixedDataModelElement import FixedDataModelElement
from aminer.parsing.DecimalIntegerValueModelElement import DecimalIntegerValueModelElement
from aminer.parsing.FixedWordlistDataModelElement import FixedWordlistDataModelElement
from aminer.parsing.SequenceModelElement import SequenceModelElement


class SequenceModelElementTest(unittest.TestCase):
    sequence_start = b'The sequence starts with a number: '
    fixed_data_model_element = FixedDataModelElement('fixed', sequence_start)
    decimal_integer_value_model_element = DecimalIntegerValueModelElement(
        'decimal', DecimalIntegerValueModelElement.SIGN_TYPE_NONE, DecimalIntegerValueModelElement.PAD_TYPE_NONE)
    fixed_wordlist_data_model_element = FixedWordlistDataModelElement('wordlist', [b' Euro', b' Dollar', b' Pfund'])
    sequence_model_element = SequenceModelElement(
        'sequence', [fixed_data_model_element, decimal_integer_value_model_element, fixed_wordlist_data_model_element])

    def test1sequence_of_matching_elements(self):
        """A normal sequence of matching elements is tested in this example test case"""
        match_context = MatchContext(b'The sequence starts with a number: 25538 Euro')
        self.assertEqual(self.sequence_model_element.get_match_element(
            'match', match_context).get_match_string(), b'The sequence starts with a number: 25538 Euro')
        self.assertEqual(match_context.match_data, b'')

    def test2sequence_not_matching(self):
        """A normal sequence of elements, which do not match with the expected sequence_model is tested."""
        match_context = MatchContext(b'The sequence starts with a number: 25538 US-Dollar')
        self.assertEqual(self.sequence_model_element.get_match_element('match', match_context), None)
        self.assertEqual(match_context.match_data, b'The sequence starts with a number: 25538 US-Dollar')

    def test3match_context_shorter_than_sequence(self):
        """This test case unit if the sequence_model returns None, when the match_context is too short for a match."""
        match_context = MatchContext(self.sequence_start)
        self.assertEqual(self.sequence_model_element.get_match_element('match', match_context), None)
        self.assertEqual(match_context.match_data, self.sequence_start)


if __name__ == "__main__":
    unittest.main()
