import unittest
from aminer.parsing.WhiteSpaceLimitedDataModelElement import WhiteSpaceLimitedDataModelElement
from unit.TestBase import TestBase, DummyMatchContext


class WhiteSpaceLimitedDataModelElementTest(TestBase):
    """Unittests for the WhiteSpaceLimitedDataModelElement."""

    id_ = "whitespace"
    path = "path"

    def test1get_id(self):
        """Test if get_id works properly."""
        whitespace_dme = WhiteSpaceLimitedDataModelElement(self.id_)
        self.assertEqual(whitespace_dme.get_id(), self.id_)

    def test2get_child_elements(self):
        """Test if get_child_elements returns None."""
        whitespace_dme = WhiteSpaceLimitedDataModelElement(self.id_)
        self.assertEqual(whitespace_dme.get_child_elements(), None)

    def test3get_match_element_valid_match(self):
        """Parse matching substring from MatchContext and check if the MatchContext was updated with all characters."""
        data = b"space: ,tab:\t"
        value = b"space:"
        match_context = DummyMatchContext(data)
        whitespace_dme = WhiteSpaceLimitedDataModelElement(self.id_)
        match_element = whitespace_dme.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, value, value, None)

        data = b"tab:\t,space: "
        value = b"tab:"
        match_context = DummyMatchContext(data)
        whitespace_dme = WhiteSpaceLimitedDataModelElement(self.id_)
        match_element = whitespace_dme.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, value, value, None)

        data = b"This+is+a+string+without+any+whitespaces."
        match_context = DummyMatchContext(data)
        whitespace_dme = WhiteSpaceLimitedDataModelElement(self.id_)
        match_element = whitespace_dme.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, data, data, None)

        data = b"This is a string with whitespaces."
        value = b"This"
        match_context = DummyMatchContext(data)
        whitespace_dme = WhiteSpaceLimitedDataModelElement(self.id_)
        match_element = whitespace_dme.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, value, value, None)

        data = b"space:  ,tab:\t"
        value = b"space:"
        match_context = DummyMatchContext(data)
        whitespace_dme = WhiteSpaceLimitedDataModelElement(self.id_)
        match_element = whitespace_dme.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, value, value, None)

        data = b"tab:\t\t,space: "
        value = b"tab:"
        match_context = DummyMatchContext(data)
        whitespace_dme = WhiteSpaceLimitedDataModelElement(self.id_)
        match_element = whitespace_dme.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, value, value, None)

        data = b"spacetab: \t,tab:\t"
        value = b"spacetab:"
        match_context = DummyMatchContext(data)
        whitespace_dme = WhiteSpaceLimitedDataModelElement(self.id_)
        match_element = whitespace_dme.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, value, value, None)

    def test4get_match_element_no_match(self):
        """Parse not matching substring from MatchContext and check if the MatchContext was not changed."""
        data = b""
        match_context = DummyMatchContext(data)
        whitespace_dme = WhiteSpaceLimitedDataModelElement(self.id_)
        match_element = whitespace_dme.get_match_element(self.path, match_context)
        self.compare_no_match_results(data, match_element, match_context)

        data = b"\ttab"
        match_context = DummyMatchContext(data)
        whitespace_dme = WhiteSpaceLimitedDataModelElement(self.id_)
        match_element = whitespace_dme.get_match_element(self.path, match_context)
        self.compare_no_match_results(data, match_element, match_context)

        data = b" space"
        match_context = DummyMatchContext(data)
        whitespace_dme = WhiteSpaceLimitedDataModelElement(self.id_)
        match_element = whitespace_dme.get_match_element(self.path, match_context)
        self.compare_no_match_results(data, match_element, match_context)

    def test5element_id_input_validation(self):
        """Check if element_id is validated."""
        self.assertRaises(ValueError, WhiteSpaceLimitedDataModelElement, "")
        self.assertRaises(TypeError, WhiteSpaceLimitedDataModelElement, None)
        self.assertRaises(TypeError, WhiteSpaceLimitedDataModelElement, b"path")
        self.assertRaises(TypeError, WhiteSpaceLimitedDataModelElement, True)
        self.assertRaises(TypeError, WhiteSpaceLimitedDataModelElement, 123)
        self.assertRaises(TypeError, WhiteSpaceLimitedDataModelElement, 123.22)
        self.assertRaises(TypeError, WhiteSpaceLimitedDataModelElement, {"id": "path"})
        self.assertRaises(TypeError, WhiteSpaceLimitedDataModelElement, ["path"])
        self.assertRaises(TypeError, WhiteSpaceLimitedDataModelElement, [])
        self.assertRaises(TypeError, WhiteSpaceLimitedDataModelElement, ())
        self.assertRaises(TypeError, WhiteSpaceLimitedDataModelElement, set())

    def test6get_match_element_match_context_input_validation(self):
        """Check if an exception is raised, when other classes than MatchContext are used in get_match_element."""
        model_element = WhiteSpaceLimitedDataModelElement(self.id_)
        data = b"space: ,tab:\t"
        model_element.get_match_element(self.path, DummyMatchContext(data))
        from aminer.parsing.MatchContext import MatchContext
        model_element.get_match_element(self.path, MatchContext(data))

        from aminer.parsing.MatchElement import MatchElement
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
