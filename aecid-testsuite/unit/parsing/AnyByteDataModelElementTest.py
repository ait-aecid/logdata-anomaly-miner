import unittest
from aminer.parsing.AnyByteDataModelElement import AnyByteDataModelElement
from aminer.parsing.MatchContext import MatchContext
from aminer.parsing.MatchElement import MatchElement
from unit.TestBase import TestBase, DummyMatchContext


class AnyByteDataModelElementTest(TestBase):
    """Unittests for the AnyByteDataModelElement."""

    id_ = "any"
    path = "path"

    def test1get_id(self):
        """Test if get_id works properly."""
        any_dme = AnyByteDataModelElement(self.id_)
        self.assertEqual(any_dme.get_id(), self.id_)

    def test2get_child_elements(self):
        """Test if get_child_elements returns None."""
        any_dme = AnyByteDataModelElement(self.id_)
        self.assertEqual(any_dme.get_child_elements(), None)

    def test3get_match_element_valid_match(self):
        """Parse matching substring from MatchContext and check if the MatchContext was updated with all characters."""
        data = b"abcdefghijklmnopqrstuvwxyz.!?"
        match_context = DummyMatchContext(data)
        any_dme = AnyByteDataModelElement(self.id_)
        match_element = any_dme.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, data, data, None)

    def test4get_match_element_no_match(self):
        """Parse not matching substring from MatchContext and check if the MatchContext was not changed."""
        data = b""
        match_context = DummyMatchContext(data)
        any_dme = AnyByteDataModelElement(self.id_)
        match_element = any_dme.get_match_element(self.path, match_context)
        self.compare_no_match_results(data, match_element, match_context)

    def test5element_id_input_validation(self):
        """Check if element_id is validated."""
        self.assertRaises(ValueError, AnyByteDataModelElement, "")  # empty element_id
        self.assertRaises(TypeError, AnyByteDataModelElement, None)  # None element_id
        self.assertRaises(TypeError, AnyByteDataModelElement, b"path")  # bytes element_id is not allowed
        self.assertRaises(TypeError, AnyByteDataModelElement, True)  # boolean element_id is not allowed
        self.assertRaises(TypeError, AnyByteDataModelElement, 123)  # integer element_id is not allowed
        self.assertRaises(TypeError, AnyByteDataModelElement, 123.22)  # float element_id is not allowed
        self.assertRaises(TypeError, AnyByteDataModelElement, {"id": "path"})  # dict element_id is not allowed
        self.assertRaises(TypeError, AnyByteDataModelElement, ["path"])  # list element_id is not allowed
        self.assertRaises(TypeError, AnyByteDataModelElement, [])  # empty list element_id is not allowed
        self.assertRaises(TypeError, AnyByteDataModelElement, ())  # empty tuple element_id is not allowed
        self.assertRaises(TypeError, AnyByteDataModelElement, set())  # empty set element_id is not allowed

    def test6get_match_element_match_context_input_validation(self):
        """Check if an exception is raised, when other classes than MatchContext are used in get_match_element."""
        model_element = AnyByteDataModelElement(self.id_)
        data = b"abcdefghijklmnopqrstuvwxyz.!?"
        model_element.get_match_element(self.path, DummyMatchContext(data))
        model_element.get_match_element(self.path, MatchContext(data))

        self.assertRaises(AttributeError, model_element.get_match_element, self.path, MatchElement(self.path, data, None, None))
        self.assertRaises(AttributeError, model_element.get_match_element, self.path, data)
        self.assertRaises(AttributeError, model_element.get_match_element, self.path, data.decode())
        self.assertRaises(AttributeError, model_element.get_match_element, self.path, 123)
        self.assertRaises(AttributeError, model_element.get_match_element, self.path, 123.22)
        self.assertRaises(AttributeError, model_element.get_match_element, self.path, True)
        self.assertRaises(AttributeError, model_element.get_match_element, self.path, None)
        self.assertRaises(AttributeError, model_element.get_match_element, self.path, [])
        self.assertRaises(AttributeError, model_element.get_match_element, self.path, {"key": MatchContext(data)})
        self.assertRaises(AttributeError, model_element.get_match_element, self.path, set())
        self.assertRaises(AttributeError, model_element.get_match_element, self.path, ())
        self.assertRaises(AttributeError, model_element.get_match_element, self.path, model_element)


if __name__ == "__main__":
    unittest.main()
