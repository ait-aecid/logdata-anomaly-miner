import unittest
from aminer.parsing.FixedDataModelElement import FixedDataModelElement
from unit.TestBase import TestBase, DummyMatchContext


class FixedDataModelElementTest(TestBase):
    """Unittests for the FixedDataModelElement."""

    data = b"fixed data. Other data."

    def test1get_id(self):
        """Test if get_id works properly."""
        fixed_dme = FixedDataModelElement("s0", b"fixed data.")
        self.assertEqual(fixed_dme.get_id(), "s0")

    def test2get_child_elements(self):
        """Test if get_child_elements returns None."""
        fixed_dme = FixedDataModelElement("s0", b"fixed data.")
        self.assertEqual(fixed_dme.get_child_elements(), None)

    def test3get_match_element_valid_match(self):
        """Parse matching substring from MatchContext and check if the MatchContext was updated accordingly."""
        fixed_string = b"fixed data."
        id_ = "path"
        path = "fixed"
        match_context = DummyMatchContext(self.data)
        fixed_dme = FixedDataModelElement(id_, fixed_string)
        match_element = fixed_dme.get_match_element(path, match_context)
        self.compare_match_results(self.data, match_element, match_context, id_, path, fixed_string, fixed_string, None)

    def test4get_match_element_no_match(self):
        """Parse not matching substring from MatchContext and check if the MatchContext was not changed."""
        no_match_string = b"Hello World."
        id_ = "path"
        path = "fixed"
        match_context = DummyMatchContext(self.data)
        fixed_dme = FixedDataModelElement(id_, no_match_string)
        match_element = fixed_dme.get_match_element(path, match_context)
        self.compare_no_match_results(self.data, match_element, match_context)

    def test5element_id_input_validation(self):
        """Check if element_id is validated."""
        fixed_string = b"string"
        # empty element_id
        element_id = ""
        self.assertRaises(ValueError, FixedDataModelElement, element_id, fixed_string)

        # None element_id
        element_id = None
        self.assertRaises(TypeError, FixedDataModelElement, element_id, fixed_string)

        # bytes element_id is not allowed
        element_id = b"path"
        self.assertRaises(TypeError, FixedDataModelElement, element_id, fixed_string)

        # integer element_id is not allowed
        element_id = 123
        self.assertRaises(TypeError, FixedDataModelElement, element_id, fixed_string)

        # float element_id is not allowed
        element_id = 123.22
        self.assertRaises(TypeError, FixedDataModelElement, element_id, fixed_string)

        # dict element_id is not allowed
        element_id = {"id": "path"}
        self.assertRaises(TypeError, FixedDataModelElement, element_id, fixed_string)

        # list element_id is not allowed
        element_id = ["path"]
        self.assertRaises(TypeError, FixedDataModelElement, element_id, fixed_string)

        # empty list element_id is not allowed
        element_id = []
        self.assertRaises(TypeError, FixedDataModelElement, element_id, fixed_string)

    def test6fixed_data_input_validation(self):
        """Check if fixed_data is validated."""
        element_id = "path"
        # empty fixed_string
        fixed_string = b""
        self.assertRaises(ValueError, FixedDataModelElement, element_id, fixed_string)

        # None fixed_string
        fixed_string = None
        self.assertRaises(TypeError, FixedDataModelElement, element_id, fixed_string)

        # string fixed_string is not allowed
        fixed_string = "path"
        self.assertRaises(TypeError, FixedDataModelElement, element_id, fixed_string)

        # integer fixed_string is not allowed
        fixed_string = 123
        self.assertRaises(TypeError, FixedDataModelElement, element_id, fixed_string)

        # float fixed_string is not allowed
        fixed_string = 123.22
        self.assertRaises(TypeError, FixedDataModelElement, element_id, fixed_string)

        # dict fixed_string is not allowed
        fixed_string = {"string": "string"}
        self.assertRaises(TypeError, FixedDataModelElement, element_id, fixed_string)

        # list fixed_string is not allowed
        fixed_string = ["path"]
        self.assertRaises(TypeError, FixedDataModelElement, element_id, fixed_string)

        # empty list fixed_string is not allowed
        fixed_string = []
        self.assertRaises(TypeError, FixedDataModelElement, element_id, fixed_string)


if __name__ == "__main__":
    unittest.main()
