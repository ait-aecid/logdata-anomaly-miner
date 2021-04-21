import unittest
from aminer.parsing.AnyByteDataModelElement import AnyByteDataModelElement
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
        # empty element_id
        element_id = ""
        self.assertRaises(ValueError, AnyByteDataModelElement, element_id)

        # None element_id
        element_id = None
        self.assertRaises(TypeError, AnyByteDataModelElement, element_id)

        # bytes element_id is not allowed
        element_id = b"path"
        self.assertRaises(TypeError, AnyByteDataModelElement, element_id)

        # bytes element_id is not allowed
        element_id = True
        self.assertRaises(TypeError, AnyByteDataModelElement, element_id)

        # integer element_id is not allowed
        element_id = 123
        self.assertRaises(TypeError, AnyByteDataModelElement, element_id)

        # float element_id is not allowed
        element_id = 123.22
        self.assertRaises(TypeError, AnyByteDataModelElement, element_id)

        # boolean element_id is not allowed
        element_id = True
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

        # empty tuple element_id is not allowed
        element_id = ()
        self.assertRaises(TypeError, AnyByteDataModelElement, element_id)

        # empty set element_id is not allowed
        element_id = set()
        self.assertRaises(TypeError, AnyByteDataModelElement, element_id)

    def test6get_match_element_match_context_input_validation(self):
        """Check if an exception is raised, when other classes than MatchContext are used in get_match_element."""
        model_element = AnyByteDataModelElement(self.id_)
        data = b"abcdefghijklmnopqrstuvwxyz.!?"
        model_element.get_match_element(self.path, DummyMatchContext(data))
        from aminer.parsing.MatchContext import MatchContext
        model_element.get_match_element(self.path, MatchContext(data))

        from aminer.parsing.MatchElement import MatchElement
        self.assertRaises(AttributeError, model_element.get_match_element, self.path, MatchElement(data, None, None, None))
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
