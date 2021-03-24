import unittest
from aminer.parsing.AnyByteDataModelElement import AnyByteDataModelElement
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
        id_ = "path"
        path = "any"
        match_context = DummyMatchContext(data)
        any_dme = AnyByteDataModelElement(id_)
        match_element = any_dme.get_match_element(path, match_context)
        self.compare_match_results(data, match_element, match_context, id_, path, data, data, None)

    def test4get_match_element_no_match(self):
        """Parse not matching substring from MatchContext and check if the MatchContext was not changed."""
        data = b""
        id_ = "path"
        path = "any"
        match_context = DummyMatchContext(data)
        any_dme = AnyByteDataModelElement(id_)
        match_element = any_dme.get_match_element(path, match_context)
        self.compare_no_match_results(data, match_element, match_context)

    def test5element_id_input_validation(self):
        """Check if element_id is validated."""
        # empty element_id
        element_id = ""
        self.assertRaises(ValueError, AnyByteDataModelElement, element_id)

        # None element_id
        element_id = None
        self.assertRaises(TypeError, AnyByteDataModelElement, element_id)

        # bytes element_id is not allowed
        element_id = b"path"
        self.assertRaises(TypeError, AnyByteDataModelElement, element_id)

        # integer element_id is not allowed
        element_id = 123
        self.assertRaises(TypeError, AnyByteDataModelElement, element_id)

        # float element_id is not allowed
        element_id = 123.22
        self.assertRaises(TypeError, AnyByteDataModelElement, element_id)

        # dict element_id is not allowed
        element_id = {"id": "path"}
        self.assertRaises(TypeError, AnyByteDataModelElement, element_id)

        # list element_id is not allowed
        element_id = ["path"]
        self.assertRaises(TypeError, AnyByteDataModelElement, element_id)

        # empty list element_id is not allowed
        element_id = []
        self.assertRaises(TypeError, AnyByteDataModelElement, element_id)


if __name__ == "__main__":
    unittest.main()
