import unittest
from aminer.parsing.MatchContext import MatchContext
from aminer.parsing.FixedDataModelElement import FixedDataModelElement
from aminer.parsing.OptionalMatchModelElement import OptionalMatchModelElement


class OptionalMatchModelElementTest(unittest.TestCase):
    """Unittests for the OptionalMatchModelElement."""

    def test1_match_element_expected(self):
        """Because of the simplicity of the FixedDataModelElement it is used to test possible outcomes of this class."""
        match_context = MatchContext(b'This is some String.')
        fixed_data_model_element = FixedDataModelElement('fixed', b'This')
        optional_match_model_element = OptionalMatchModelElement('optional', fixed_data_model_element)
        self.assertEqual(optional_match_model_element.get_match_element('match', match_context).get_match_string(), b'This')
        self.assertEqual(match_context.match_data, b' is some String.')

    def test2_match_element_empty(self):
        """An Empty MatchElement is expected, due to not finding the fixed String. The MatchContext must not be changed."""
        match_context = MatchContext(b'Another String.')
        fixed_data_model_element = FixedDataModelElement('fixed', b'This')
        optional_match_model_element = OptionalMatchModelElement('optional', fixed_data_model_element)
        self.assertEqual(optional_match_model_element.get_match_element('match', match_context).get_match_string(), '')
        self.assertEqual(match_context.match_data, b'Another String.')


if __name__ == "__main__":
    unittest.main()
