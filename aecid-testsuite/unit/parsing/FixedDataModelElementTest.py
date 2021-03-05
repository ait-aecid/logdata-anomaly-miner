import unittest
from aminer.parsing.FixedDataModelElement import FixedDataModelElement
from unit.TestBase import TestBase, DummyMatchContext


class FixedDataModelElementTest(TestBase):
    """Unittests for the FixedDataModelElement."""

    data = b"fixed data. Other data."

    def test1get_match_element_valid_match(self):
        """Parse matching substring from MatchContext and check if the MatchContext was updated accordingly."""
        fixed_string = b'fixed data.'
        dummy_match_context = DummyMatchContext(self.data)
        fixed_dme = FixedDataModelElement("s0", fixed_string)
        match_element = fixed_dme.get_match_element("fixed", dummy_match_context)
        self.assertEqual(match_element.path, "fixed/s0")
        self.assertEqual(match_element.match_string, fixed_string)
        self.assertEqual(match_element.match_object, fixed_string)
        self.assertIsNone(match_element.children, None)
        self.assertEqual(dummy_match_context.match_data, fixed_string)

    def test2get_match_element_no_match(self):
        """Parse not matching substring from MatchContext and check if the MatchContext was not changed."""
        no_match_string = b"Hello World."
        dummy_match_context = DummyMatchContext(self.data)
        fixed_dme = FixedDataModelElement("s0", no_match_string)
        match_element = fixed_dme.get_match_element("fixed", dummy_match_context)
        self.assertIsNone(match_element, None)
        self.assertEqual(dummy_match_context.match_data, self.data)

    def test3element_id_input_validation(self):
        """Check if element_id is validated."""
        fixed_string = b"string"
        # empty element_id
        element_id = ""
        self.assertRaises(ValueError, FixedDataModelElement, element_id, fixed_string)

        # bytes element_id is not allowed
        element_id = b"path"
        self.assertRaises(ValueError, FixedDataModelElement, element_id, fixed_string)

        # integer element_id is not allowed
        element_id = 123
        self.assertRaises(ValueError, FixedDataModelElement, element_id, fixed_string)

        # float element_id is not allowed
        element_id = 123.22
        self.assertRaises(ValueError, FixedDataModelElement, element_id, fixed_string)

        # dict element_id is not allowed
        element_id = {"id": "path"}
        self.assertRaises(ValueError, FixedDataModelElement, element_id, fixed_string)

        # list element_id is not allowed
        element_id = ["path"]
        self.assertRaises(ValueError, FixedDataModelElement, element_id, fixed_string)

    def test4fixed_data_input_validation(self):
        """Check if fixed_data is validated."""

    pid = b' pid='

    # def test1_valid_input_with_match_element_found(self):
    #     """
    #     This testmethod is part of the Basis Path Testing / Decision Coverage.
    #     It assures, that the intended usage of the FixedDataModelElement is working. (MatchElement found)
    #     """
    #     match_context = MatchContext(self.pid)
    #     fixed_dme = FixedDataModelElement('s0', self.pid)
    #     match_element = fixed_dme.get_match_element("", match_context)
    #     self.assertNotEqual(match_element, None, "There should exist a MatchElement!")
    #
    # def test2_valid_input_with_match_element_not_found(self):
    #     """
    #     This testmethod is part of the Basis Path Testing / Decision Coverage.
    #     It assures, that the intended usage of the FixedDataModelElement is working. (MatchElement not found)
    #     """
    #     match_context = MatchContext(b'This is some other row in the logs')
    #     fixed_dme = FixedDataModelElement('s0', self.pid)
    #     match_element = fixed_dme.get_match_element("", match_context)
    #     self.assertEqual(match_element, None, "There should not exist a MatchElement!")
    #
    # def test3_fuzzing_input_no_bytestring(self):
    #     """
    #     This testmethod is part of the Fuzz Testing.
    #     It assures, that the data type of the fixed_data-input is validated by the __init__ method.
    #     """
    #     self.assertRaises(Exception, FixedDataModelElement, 's0', self.pid.decode())
    #
    # def test4_fuzzing_path_is_none(self):
    #     """
    #     This testmethod is part of the Fuzz Testing and it assures, that the path-input is validated.
    #     In this case a path is not needed, because FixedDataModelElement has no child elements.
    #     """
    #     match_context = MatchContext(self.pid)
    #     fixed_dme = FixedDataModelElement('s0', self.pid)
    #     match_element = fixed_dme.get_match_element(None, match_context)
    #     self.assertNotEqual(match_element, None, "There should exist a MatchElement!")

    # skipcq: PYL-W0105
    '''
    def test5FuzzingMatchContextNoBytestring(self):
        """This testmethod is part of the Fuzz Testing and it assures, that the match_data-input of MatchContext is validated by the
        constructor. MatchData must be of the type bytestring else the startswith method raises an TypeErrorException. To show this
        behavior comment the first two lines and uncomment the remaining code. """
        self.assertRaises(Exception, MatchContext, ' pid=')
        self.matchContext = MatchContext(' pid=')
        self.fixedDME = FixedDataModelElement('s0', self.pid)
        self.matchElement = self.fixedDME.getMatchElement("", self.matchContext)
    '''


if __name__ == "__main__":
    unittest.main()
