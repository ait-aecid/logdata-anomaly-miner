import unittest
from aminer.parsing.AnyByteDataModelElement import AnyByteDataModelElement
from aminer.parsing.MatchContext import MatchContext
from unit.TestBase import TestBase, DummyMatchContext


class AnyByteDataModelElementTest(TestBase):
    """Unittests for the AnyByteDataModelElement."""

    def test1get_id(self):
        """Test if get_id works properly."""
        any_dme = AnyByteDataModelElement("s0")
        self.assertEqual(any_dme.get_id(), "s0")

    def test2get_child_elements(self):
        """Test if get_child_elements returns None."""
        any_dme = AnyByteDataModelElement("s0")
        self.assertEqual(any_dme.get_child_elements(), None)

    def test3get_match_element_valid_match(self):
        """Parse matching substring from MatchContext and check if the MatchContext was updated accordingly."""
        data = b'abcdefghijklmnopqrstuvwxyz.!?'
        dummy_match_context = DummyMatchContext(data)
        any_dme = AnyByteDataModelElement("s0")
        match_element = any_dme.get_match_element("any", dummy_match_context)
        self.assertEqual(match_element.path, "any/s0")
        self.assertEqual(match_element.match_string, data)
        self.assertEqual(match_element.match_object, data)
        self.assertIsNone(match_element.children, None)
        self.assertEqual(dummy_match_context.match_data, data)

    def test4get_match_element_no_match(self):
        """Parse not matching substring from MatchContext and check if the MatchContext was not changed."""
        no_match_string = b""
        dummy_match_context = DummyMatchContext(no_match_string)
        any_dme = AnyByteDataModelElement("s0")
        match_element = any_dme.get_match_element("any", dummy_match_context)
        self.assertIsNone(match_element, None)
        self.assertEqual(dummy_match_context.match_data, no_match_string)

    def test5element_id_input_validation(self):
        """Check if element_id is validated."""
        # empty element_id
        element_id = ""
        self.assertRaises(ValueError, AnyByteDataModelElement, element_id)

        # bytes element_id is not allowed
        element_id = b"path"
        self.assertRaises(ValueError, AnyByteDataModelElement, element_id)

        # integer element_id is not allowed
        element_id = 123
        self.assertRaises(ValueError, AnyByteDataModelElement, element_id)

        # float element_id is not allowed
        element_id = 123.22
        self.assertRaises(ValueError, AnyByteDataModelElement, element_id)

        # dict element_id is not allowed
        element_id = {"id": "path"}
        self.assertRaises(ValueError, AnyByteDataModelElement, element_id)

        # list element_id is not allowed
        element_id = ["path"]
        self.assertRaises(ValueError, AnyByteDataModelElement, element_id)


if __name__ == "__main__":
    unittest.main()
