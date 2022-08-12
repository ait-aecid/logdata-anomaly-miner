import unittest
from aminer.parsing.VariableByteDataModelElement import VariableByteDataModelElement
from aminer.parsing.MatchContext import MatchContext
from aminer.parsing.MatchElement import MatchElement
from unit.TestBase import TestBase, DummyMatchContext


class VariableByteDataModelElementTest(TestBase):
    """Unittests for the VariableByteDataModelElement."""

    id_ = "variable"
    path = "path"
    alphabet = b"abcdefghijklmnopqrstuvwxyz "

    def test1get_match_element_valid_match(self):
        """Parse matching substring from MatchContext and check if the MatchContext was updated with all characters."""
        data = b"abcdefghijklm nopqrstuvwxyz.!?"
        value = b"abcdefghijklm nopqrstuvwxyz"
        match_context = DummyMatchContext(data)
        variable_byte_dme = VariableByteDataModelElement(self.id_, self.alphabet)
        match_element = variable_byte_dme.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, value, value, None)

    def test2get_match_element_no_match(self):
        """Parse not matching substring from MatchContext and check if the MatchContext was not changed."""
        data = b""
        match_context = DummyMatchContext(data)
        variable_byte_dme = VariableByteDataModelElement(self.id_, self.alphabet)
        match_element = variable_byte_dme.get_match_element(self.path, match_context)
        self.compare_no_match_results(data, match_element, match_context)

        data = b"!abcdefghijklm nopqrstuvwxyz.!?"
        match_context = DummyMatchContext(data)
        variable_byte_dme = VariableByteDataModelElement(self.id_, self.alphabet)
        match_element = variable_byte_dme.get_match_element(self.path, match_context)
        self.compare_no_match_results(data, match_element, match_context)

    def test3element_id_input_validation(self):
        """Check if element_id is validated."""
        self.assertRaises(ValueError, VariableByteDataModelElement, "", self.alphabet)
        self.assertRaises(TypeError, VariableByteDataModelElement, None, self.alphabet)
        self.assertRaises(TypeError, VariableByteDataModelElement, b"path", self.alphabet)
        self.assertRaises(TypeError, VariableByteDataModelElement, True, self.alphabet)
        self.assertRaises(TypeError, VariableByteDataModelElement, 123, self.alphabet)
        self.assertRaises(TypeError, VariableByteDataModelElement, 123.22, self.alphabet)
        self.assertRaises(TypeError, VariableByteDataModelElement, {"id": "path"}, self.alphabet)
        self.assertRaises(TypeError, VariableByteDataModelElement, ["path"], self.alphabet)
        self.assertRaises(TypeError, VariableByteDataModelElement, [], self.alphabet)
        self.assertRaises(TypeError, VariableByteDataModelElement, (), self.alphabet)
        self.assertRaises(TypeError, VariableByteDataModelElement, set(), self.alphabet)

    def test4alphabet_input_validation(self):
        """Check if element_id is validated."""
        self.assertRaises(TypeError, VariableByteDataModelElement, self.id_, "string")
        self.assertRaises(TypeError, VariableByteDataModelElement, self.id_, None)
        self.assertRaises(ValueError, VariableByteDataModelElement, self.id_, b"")
        self.assertRaises(TypeError, VariableByteDataModelElement, self.id_, True)
        self.assertRaises(TypeError, VariableByteDataModelElement, self.id_, 123)
        self.assertRaises(TypeError, VariableByteDataModelElement, self.id_, 123.22)
        self.assertRaises(TypeError, VariableByteDataModelElement, self.id_, {"id": "path"})
        self.assertRaises(TypeError, VariableByteDataModelElement, self.id_, ["path"])
        self.assertRaises(TypeError, VariableByteDataModelElement, self.id_, [])
        self.assertRaises(TypeError, VariableByteDataModelElement, self.id_, ())
        self.assertRaises(TypeError, VariableByteDataModelElement, self.id_, set())

    def test5get_match_element_match_context_input_validation(self):
        """Check if an exception is raised, when other classes than MatchContext are used in get_match_element."""
        model_element = VariableByteDataModelElement(self.id_, self.alphabet)
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
