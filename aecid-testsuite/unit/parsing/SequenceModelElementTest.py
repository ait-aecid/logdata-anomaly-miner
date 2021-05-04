import unittest
from aminer.parsing.MatchContext import MatchContext
from aminer.parsing.MatchElement import MatchElement
from aminer.parsing.SequenceModelElement import SequenceModelElement
from unit.TestBase import TestBase, DummyMatchContext, DummyFixedDataModelElement


class SequenceModelElementTest(TestBase):
    """Unittests for the SequenceModelElement."""

    id_ = "sequence"
    path = "path"
    children = [DummyFixedDataModelElement("0", b"string0 "), DummyFixedDataModelElement("1", b"string1 "),
                DummyFixedDataModelElement("2", b"string2")]
    match_elements = [MatchElement("path/sequence/0", b"string0 ", b"string0 ", None),
                      MatchElement("path/sequence/1", b"string1 ", b"string1 ", None),
                      MatchElement("path/sequence/2", b"string2", b"string2", None)]

    def test1get_id(self):
        """Test if get_id works properly."""
        sequence_me = SequenceModelElement(self.id_, self.children)
        self.assertEqual(sequence_me.get_id(), self.id_)

    def test2get_child_elements(self):
        """Test if get_child_elements returns None."""
        sequence_me = SequenceModelElement(self.id_, self.children)
        self.assertEqual(sequence_me.get_child_elements(), self.children)

    def test3get_match_element_valid_match(self):
        """Parse matching substring from MatchContext and check if the MatchContext was updated with all characters."""
        data = b"string0 string1 string2"
        match_context = DummyMatchContext(data)
        sequence_me = SequenceModelElement(self.id_, self.children)
        match_element = sequence_me.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, data, data, self.match_elements)

        data = b"string0 string1 string2 other string follows"
        value = b"string0 string1 string2"
        match_context = DummyMatchContext(data)
        sequence_me = SequenceModelElement(self.id_, self.children)
        match_element = sequence_me.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, value, value, self.match_elements)

    def test4get_match_element_no_match(self):
        """Parse not matching substring from MatchContext and check if the MatchContext was not changed."""
        data = b""
        match_context = DummyMatchContext(data)
        sequence_me = SequenceModelElement(self.id_, self.children)
        match_element = sequence_me.get_match_element(self.path, match_context)
        self.compare_no_match_results(data, match_element, match_context)

        data = b"string0 string1 "
        match_context = DummyMatchContext(data)
        sequence_me = SequenceModelElement(self.id_, self.children)
        match_element = sequence_me.get_match_element(self.path, match_context)
        self.compare_no_match_results(data, match_element, match_context)

        data = b"string0 string1 string3"
        match_context = DummyMatchContext(data)
        sequence_me = SequenceModelElement(self.id_, self.children)
        match_element = sequence_me.get_match_element(self.path, match_context)
        self.compare_no_match_results(data, match_element, match_context)

        data = b"string0 string0 string2"
        match_context = DummyMatchContext(data)
        sequence_me = SequenceModelElement(self.id_, self.children)
        match_element = sequence_me.get_match_element(self.path, match_context)
        self.compare_no_match_results(data, match_element, match_context)

    def test5element_id_input_validation(self):
        """Check if element_id is validated."""
        self.assertRaises(ValueError, SequenceModelElement, "", self.children)
        self.assertRaises(TypeError, SequenceModelElement, None, self.children)
        self.assertRaises(TypeError, SequenceModelElement, b"path", self.children)
        self.assertRaises(TypeError, SequenceModelElement, True, self.children)
        self.assertRaises(TypeError, SequenceModelElement, 123, self.children)
        self.assertRaises(TypeError, SequenceModelElement, 123.22, self.children)
        self.assertRaises(TypeError, SequenceModelElement, {"id": "path"}, self.children)
        self.assertRaises(TypeError, SequenceModelElement, ["path"], self.children)
        self.assertRaises(TypeError, SequenceModelElement, [], self.children)
        self.assertRaises(TypeError, SequenceModelElement, (), self.children)
        self.assertRaises(TypeError, SequenceModelElement, set(), self.children)

    def test6get_match_element_match_context_input_validation(self):
        """Check if an exception is raised, when other classes than MatchContext are used in get_match_element."""
        model_element = SequenceModelElement(self.id_, self.children)
        data = b"string0 string1 string2"
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
