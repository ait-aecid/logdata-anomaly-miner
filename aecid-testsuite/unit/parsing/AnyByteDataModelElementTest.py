import unittest
from aminer.parsing.AnyByteDataModelElement import AnyByteDataModelElement
from aminer.parsing.MatchContext import MatchContext


class AnyByteDataModelElementTest(unittest.TestCase):

    def test1get_match_element_valid_input(self):
        """This test case checks if VALID inputs are accepted."""
        match_context = MatchContext(b' some input 123 }')
        any_byte_date_me = AnyByteDataModelElement('id')
        self.assertEqual(any_byte_date_me.get_match_element('match1', match_context).get_match_string(), b' some input 123 }')
        self.assertEqual(any_byte_date_me.get_match_element('match1', match_context), None)
        match_context = MatchContext(b'1    ')
        self.assertEqual(any_byte_date_me.get_match_element('match1', match_context).get_match_string(), b'1    ')

    def test2get_match_element_invalid_input(self):
        """This test case checks if INVALID inputs are accepted."""
        match_context = MatchContext(b'')
        any_byte_date_me = AnyByteDataModelElement('id')
        self.assertEqual(any_byte_date_me.get_match_element('match1', match_context), None)

        match_context = MatchContext(None)
        self.assertEqual(any_byte_date_me.get_match_element('match1', match_context), None)


if __name__ == "__main__":
    unittest.main()
