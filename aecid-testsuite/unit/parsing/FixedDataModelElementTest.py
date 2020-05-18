import unittest
from aminer.parsing.FixedDataModelElement import FixedDataModelElement
from aminer.parsing.MatchContext import MatchContext


class FixedDataModelElementTest(unittest.TestCase):
    pid = b' pid='

    def test1_valid_input_with_match_element_found(self):
        """This testmethod is part of the Basis Path Testing / Decision Coverage. It assures, that the intended usage of the
        FixedDataModelElement is working. (MatchElement found)"""
        match_context = MatchContext(self.pid)
        fixed_dme = FixedDataModelElement('s0', self.pid)
        match_element = fixed_dme.get_match_element("", match_context)
        self.assertNotEqual(match_element, None, "There should exist a MatchElement!")

    def test2_valid_input_with_match_element_not_found(self):
        """This testmethod is part of the Basis Path Testing / Decision Coverage. It assures, that the intended usage of the
        FixedDataModelElement is working. (MatchElement not found)"""
        match_context = MatchContext(b'This is some other row in the logs')
        fixed_dme = FixedDataModelElement('s0', self.pid)
        match_element = fixed_dme.get_match_element("", match_context)
        self.assertEqual(match_element, None, "There should not exist a MatchElement!")

    def test3_fuzzing_input_no_bytestring(self):
        """This testmethod is part of the Fuzz Testing and it assures, that the data type of the fixed_data-input is validated by the
        constructur."""
        self.assertRaises(Exception, FixedDataModelElement, 's0', self.pid.decode())

    def test4_fuzzing_path_is_none(self):
        """This testmethod is part of the Fuzz Testing and it assures, that the path-input is validated. In this case a path is not
        needed, because FixedDataModelElement has no child elements."""
        match_context = MatchContext(self.pid)
        fixed_dme = FixedDataModelElement('s0', self.pid)
        match_element = fixed_dme.get_match_element(None, match_context)
        self.assertNotEqual(match_element, None, "There should exist a MatchElement!")


'''
    def test5FuzzingMatchContextNoBytestring(self):
        """This testmethod is part of the Fuzz Testing and it assures, that the match_data-input of MatchContext is validated by the
        constructor. MatchData must be of the type bytestring else the startswith method raises an TypeErrorException. To show this
        behavior comment the first two lines and uncomment the remaining code. """
        self.assertRaises(Exception, MatchContext, ' pid=')
#        self.matchContext = MatchContext(' pid=')
#        self.fixedDME = FixedDataModelElement('s0', self.pid)
#        self.matchElement = self.fixedDME.getMatchElement("", self.matchContext)
'''


if __name__ == "__main__":
    unittest.main()
