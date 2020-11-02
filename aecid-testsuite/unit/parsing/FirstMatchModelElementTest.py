import unittest
from aminer.parsing.MatchContext import MatchContext
from aminer.parsing.DecimalIntegerValueModelElement import DecimalIntegerValueModelElement
from aminer.parsing.FirstMatchModelElement import FirstMatchModelElement
from aminer.parsing.FixedDataModelElement import FixedDataModelElement


class FirstDataModelElementTest(unittest.TestCase):
    """Unittests for the FirstDataModelElement."""

    string = b'25537 uid=2'
    wrong_match_element = 'Wrong MatchElement'

    def test1single_match(self):
        """This test case proves the intended functionality of single Matches."""
        match_context = MatchContext(self.string)
        decimal_integer_value_me = DecimalIntegerValueModelElement(
            None, DecimalIntegerValueModelElement.SIGN_TYPE_NONE, DecimalIntegerValueModelElement.PAD_TYPE_NONE)
        fixed_dme = FixedDataModelElement('s0', b'pid=')
        first_match_model_element = FirstMatchModelElement('first', [decimal_integer_value_me, fixed_dme])
        self.assertEqual(
            first_match_model_element.get_match_element('first', match_context).get_match_string(), b'25537', self.wrong_match_element)

        match_context = MatchContext(b'pid=')
        first_match_model_element = FirstMatchModelElement('first', [decimal_integer_value_me, fixed_dme])
        self.assertEqual(
            first_match_model_element.get_match_element('first', match_context).get_match_string(), b'pid=', self.wrong_match_element)

    def test2no_match(self):
        """This test case checks if no match is returned when no child element matches."""
        match_context = MatchContext(b'pid = 25537 uid=2')
        decimal_integer_value_me = DecimalIntegerValueModelElement(
            None, DecimalIntegerValueModelElement.SIGN_TYPE_NONE, DecimalIntegerValueModelElement.PAD_TYPE_NONE)
        fixed_dme = FixedDataModelElement('s0', b'pid=')
        first_match_model_element = FirstMatchModelElement('first', [decimal_integer_value_me, fixed_dme])
        self.assertEqual(first_match_model_element.get_match_element('first', match_context), None, 'No MatchElement was expected')

    def test3double_match(self):
        """This test case checks if the first match is returned, when multiple children match."""
        match_context = MatchContext(self.string)
        decimal_integer_value_me = DecimalIntegerValueModelElement(
            None, DecimalIntegerValueModelElement.SIGN_TYPE_NONE, DecimalIntegerValueModelElement.PAD_TYPE_NONE)
        fixed_dme = FixedDataModelElement('s0', self.string)
        first_match_model_element = FirstMatchModelElement('first', [decimal_integer_value_me, fixed_dme])
        self.assertEqual(
            first_match_model_element.get_match_element('first', match_context).get_match_string(), b'25537', self.wrong_match_element)

        match_context = MatchContext(self.string)
        first_match_model_element = FirstMatchModelElement('first', [fixed_dme, decimal_integer_value_me])
        self.assertEqual(
            first_match_model_element.get_match_element('first', match_context).get_match_string(), self.string, self.wrong_match_element)

    def test4child_elements(self):
        """This test case checks if all child elements are added as expected."""
        decimal_integer_value_me = DecimalIntegerValueModelElement(
            None, DecimalIntegerValueModelElement.SIGN_TYPE_NONE, DecimalIntegerValueModelElement.PAD_TYPE_NONE)
        fixed_dme = FixedDataModelElement('s0', self.string)
        first_match_model_element = FirstMatchModelElement('first', [decimal_integer_value_me, fixed_dme])
        self.assertEqual(
            first_match_model_element.get_child_elements(), [decimal_integer_value_me, fixed_dme], 'ChildElements not as expected')
        self.assertRaises(Exception, FirstMatchModelElement('first', []))


if __name__ == "__main__":
    unittest.main()
