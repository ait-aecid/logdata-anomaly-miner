import unittest
from aminer.parsing.FirstMatchModelElement import FirstMatchModelElement
from aminer.parsing.MatchContext import MatchContext
from aminer.parsing.MatchElement import MatchElement
from unit.TestBase import TestBase, DummyMatchContext, DummyFixedDataModelElement


class FirstDataModelElementTest(TestBase):
    """Unittests for the FirstDataModelElement."""

    id_ = "first"
    path = "path"
    me1 = DummyFixedDataModelElement("me1", b"The first fixed string.")
    me2 = DummyFixedDataModelElement("me2", b"Random string23.")
    me3 = DummyFixedDataModelElement("me3", b"Random string2")
    children = [me1, me2, me3]

    def test1get_id(self):
        """Test if get_id works properly."""
        first_match_me = FirstMatchModelElement(self.id_, self.children)
        self.assertEqual(first_match_me.get_id(), self.id_)

    def test2get_child_elements(self):
        """Test if get_child_elements returns None."""
        first_match_me = FirstMatchModelElement(self.id_, self.children)
        self.assertEqual(first_match_me.get_child_elements(), self.children)

    def test3get_match_element_valid_match(self):
        """Parse matching substring from MatchContext and check if the MatchContext was updated with all characters."""
        data = b"The first fixed string. Random string23."
        value = b"The first fixed string."
        match_context = DummyMatchContext(data)
        first_match_me = FirstMatchModelElement(self.id_, self.children)
        match_element = first_match_me.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_+"/me1", self.path, value, value, None)

        data = b"Random string23. Random string23."
        value = b"Random string23."
        match_context = DummyMatchContext(data)
        first_match_me = FirstMatchModelElement(self.id_, self.children)
        match_element = first_match_me.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_ + "/me2", self.path, value, value, None)

        data = b"Random string2 Random string23."
        value = b"Random string2"
        match_context = DummyMatchContext(data)
        first_match_me = FirstMatchModelElement(self.id_, self.children)
        match_element = first_match_me.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_ + "/me3", self.path, value, value, None)

        data = b"Random string24. Random string23."
        value = b"Random string2"
        match_context = DummyMatchContext(data)
        first_match_me = FirstMatchModelElement(self.id_, self.children)
        match_element = first_match_me.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_ + "/me3", self.path, value, value, None)

    def test4get_match_element_no_match(self):
        """Parse not matching substring from MatchContext and check if the MatchContext was not changed."""
        data = b"some none matching string"
        match_context = DummyMatchContext(data)
        first_match_me = FirstMatchModelElement(self.id_, self.children)
        match_element = first_match_me.get_match_element(self.path, match_context)
        self.compare_no_match_results(data, match_element, match_context)

        data = b"The first fixed string"
        match_context = DummyMatchContext(data)
        first_match_me = FirstMatchModelElement(self.id_, self.children)
        match_element = first_match_me.get_match_element(self.path, match_context)
        self.compare_no_match_results(data, match_element, match_context)

        data = b"Random string42"
        match_context = DummyMatchContext(data)
        first_match_me = FirstMatchModelElement(self.id_, self.children)
        match_element = first_match_me.get_match_element(self.path, match_context)
        self.compare_no_match_results(data, match_element, match_context)

    def test5element_id_input_validation(self):
        """Check if element_id is validated."""
        self.assertRaises(ValueError, FirstMatchModelElement, "", self.children)  # empty element_id
        self.assertRaises(TypeError, FirstMatchModelElement, None, self.children)  # None element_id
        self.assertRaises(TypeError, FirstMatchModelElement, b"path", self.children)  # bytes element_id is not allowed
        self.assertRaises(TypeError, FirstMatchModelElement, True, self.children)  # boolean element_id is not allowed
        self.assertRaises(TypeError, FirstMatchModelElement, 123, self.children)  # integer element_id is not allowed
        self.assertRaises(TypeError, FirstMatchModelElement, 123.22, self.children)  # float element_id is not allowed
        self.assertRaises(TypeError, FirstMatchModelElement, {"id": "path"}, self.children)  # dict element_id is not allowed
        self.assertRaises(TypeError, FirstMatchModelElement, ["path"], self.children)  # list element_id is not allowed
        self.assertRaises(TypeError, FirstMatchModelElement, [], self.children)  # empty list element_id is not allowed
        self.assertRaises(TypeError, FirstMatchModelElement, (), self.children)  # empty tuple element_id is not allowed
        self.assertRaises(TypeError, FirstMatchModelElement, set(), self.children)  # empty set element_id is not allowed

    def test6children_input_validation(self):
        """Check if children is validated."""
        self.assertRaises(TypeError, FirstMatchModelElement, self.id_, "path")  # string children
        self.assertRaises(TypeError, FirstMatchModelElement, self.id_, None)  # None children
        self.assertRaises(TypeError, FirstMatchModelElement, self.id_, b"path")  # bytes children is not allowed
        self.assertRaises(TypeError, FirstMatchModelElement, self.id_, True)  # boolean children is not allowed
        self.assertRaises(TypeError, FirstMatchModelElement, self.id_, 123)  # integer children is not allowed
        self.assertRaises(TypeError, FirstMatchModelElement, self.id_, 123.22)  # float children is not allowed
        self.assertRaises(TypeError, FirstMatchModelElement, self.id_, {"id": "path"})  # dict children is not allowed
        # list children with no ModelElementInterface elements is not allowed
        self.assertRaises(TypeError, FirstMatchModelElement, self.id_, ["path"])
        self.assertRaises(ValueError, FirstMatchModelElement, self.id_, [])  # empty list children is not allowed
        self.assertRaises(TypeError, FirstMatchModelElement, self.id_, ())  # empty tuple children is not allowed
        self.assertRaises(TypeError, FirstMatchModelElement, self.id_, set())  # empty set children is not allowed

    def test7get_match_element_match_context_input_validation(self):
        """Check if an exception is raised, when other classes than MatchContext are used in get_match_element."""
        model_element = FirstMatchModelElement(self.id_, self.children)
        data = b"abcdefghijklmnopqrstuvwxyz.!?"
        model_element.get_match_element(self.path, DummyMatchContext(data))
        model_element.get_match_element(self.path, MatchContext(data))

        self.assertRaises(AttributeError, model_element.get_match_element, self.path, MatchElement(None, data, None, None))
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
