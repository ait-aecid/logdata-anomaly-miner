import unittest
from aminer.parsing.FixedDataModelElement import FixedDataModelElement
from unit.TestBase import TestBase, DummyMatchContext


class FixedDataModelElementTest(TestBase):
    """Unittests for the FixedDataModelElement."""

    data = b"fixed data. Other data."

    def test1get_id(self):
        """Test if get_id works properly."""
        fixed_dme = FixedDataModelElement("s0", b'fixed data.')
        self.assertEqual(fixed_dme.get_id(), "s0")

    def test2get_child_elements(self):
        """Test if get_child_elements returns None."""
        fixed_dme = FixedDataModelElement("s0", b'fixed data.')
        self.assertEqual(fixed_dme.get_child_elements(), None)

    def test3get_match_element_valid_match(self):
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

    def test4get_match_element_no_match(self):
        """Parse not matching substring from MatchContext and check if the MatchContext was not changed."""
        no_match_string = b"Hello World."
        dummy_match_context = DummyMatchContext(self.data)
        fixed_dme = FixedDataModelElement("s0", no_match_string)
        match_element = fixed_dme.get_match_element("fixed", dummy_match_context)
        self.assertIsNone(match_element, None)
        self.assertEqual(dummy_match_context.match_data, self.data)

    def test5element_id_input_validation(self):
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

    def test6fixed_data_input_validation(self):
        """Check if fixed_data is validated."""
        element_id = "path"
        # empty fixed_string
        fixed_string = b""
        self.assertRaises(ValueError, FixedDataModelElement, element_id, fixed_string)

        # string fixed_string is not allowed
        fixed_string = "path"
        self.assertRaises(ValueError, FixedDataModelElement, element_id, fixed_string)

        # integer fixed_string is not allowed
        fixed_string = 123
        self.assertRaises(ValueError, FixedDataModelElement, element_id, fixed_string)

        # float fixed_string is not allowed
        fixed_string = 123.22
        self.assertRaises(ValueError, FixedDataModelElement, element_id, fixed_string)

        # dict fixed_string is not allowed
        fixed_string = {"string": "string"}
        self.assertRaises(ValueError, FixedDataModelElement, element_id, fixed_string)

        # list fixed_string is not allowed
        fixed_string = ["path"]
        self.assertRaises(ValueError, FixedDataModelElement, element_id, fixed_string)


if __name__ == "__main__":
    unittest.main()
