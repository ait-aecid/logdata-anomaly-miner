import unittest
from aminer.parsing.DelimitedDataModelElement import DelimitedDataModelElement
from aminer.parsing.MatchContext import MatchContext
from aminer.parsing.MatchElement import MatchElement
from unit.TestBase import TestBase, DummyMatchContext


class DelimitedDataModelElementTest(TestBase):
    """Unittests for the DelimitedDataModelElement."""

    id_ = "delimited"
    path = "path"
    delimiter = b","

    def test1get_id(self):
        """Test if get_id works properly."""
        delimited_data_me = DelimitedDataModelElement(self.id_, self.delimiter)
        self.assertEqual(delimited_data_me.get_id(), self.id_)

    def test2get_child_elements(self):
        """Test if get_child_elements returns None."""
        delimited_data_me = DelimitedDataModelElement(self.id_, self.delimiter)
        self.assertEqual(delimited_data_me.get_child_elements(), None)

    def test3get_match_element_single_char(self):
        """A single character is used as delimiter and not consumed (consume_delimiter=False)."""
        data = b"this is a match context.\n"

        delimited_data_model_element = DelimitedDataModelElement(self.id_, b"a")
        value = b"this is "
        match_context = DummyMatchContext(data)
        match_element = delimited_data_model_element.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, value, value, None)

        delimited_data_model_element = DelimitedDataModelElement(self.id_, b"c")
        value = b"this is a mat"
        match_context = DummyMatchContext(data)
        match_element = delimited_data_model_element.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, value, value, None)

        delimited_data_model_element = DelimitedDataModelElement(self.id_, b"e")
        value = b"this is a match cont"
        match_context = DummyMatchContext(data)
        match_element = delimited_data_model_element.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, value, value, None)

        delimited_data_model_element = DelimitedDataModelElement(self.id_, b"\n")
        value = b"this is a match context."
        match_context = DummyMatchContext(data)
        match_element = delimited_data_model_element.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, value, value, None)

    def test4get_match_element_single_char_no_match(self):
        """A single character is used as delimiter and not matched."""
        data = b"this is a match context.\n"
        for char in "bdfgjklpqruvwyz":
            delimited_data_model_element = DelimitedDataModelElement(self.id_, char.encode())
            match_context = DummyMatchContext(data)
            match_element = delimited_data_model_element.get_match_element(self.path, match_context)
            self.compare_no_match_results(data, match_element, match_context)

    def test5delimiter_string(self):
        """In this test case a whole string is searched for in the match_data and  it is not consumed (consume_delimiter=False)."""
        data = b"this is a match context.\n"

        value = b"this"
        match_context = DummyMatchContext(data)
        delimited_data_model_element = DelimitedDataModelElement(self.id_, b" is")
        match_element = delimited_data_model_element.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, value, value, None)

        value = b"th"
        match_context = DummyMatchContext(data)
        delimited_data_model_element = DelimitedDataModelElement(self.id_, b"is")
        match_element = delimited_data_model_element.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, value, value, None)

        value = b"this is a match "
        match_context = DummyMatchContext(data)
        delimited_data_model_element = DelimitedDataModelElement(self.id_, b"context.\n")
        match_element = delimited_data_model_element.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, value, value, None)

        value = b"t"
        match_context = DummyMatchContext(data)
        delimited_data_model_element = DelimitedDataModelElement(self.id_, b"his is a match context.\n")
        match_element = delimited_data_model_element.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, value, value, None)

    def test6delimiter_string_no_match(self):
        """In this test case a whole string is searched for in the match_data with no match."""
        data = b"this is a match context.\n"

        match_context = DummyMatchContext(data)
        delimited_data_model_element = DelimitedDataModelElement(self.id_, b"other data")
        match_element = delimited_data_model_element.get_match_element(self.path, match_context)
        self.compare_no_match_results(data, match_element, match_context)

        match_context = DummyMatchContext(data)
        delimited_data_model_element = DelimitedDataModelElement(self.id_, b"isa")
        match_element = delimited_data_model_element.get_match_element(self.path, match_context)
        self.compare_no_match_results(data, match_element, match_context)

        match_context = DummyMatchContext(data)
        delimited_data_model_element = DelimitedDataModelElement(self.id_, b"context\n")
        match_element = delimited_data_model_element.get_match_element(self.path, match_context)
        self.compare_no_match_results(data, match_element, match_context)

        match_context = DummyMatchContext(data)
        delimited_data_model_element = DelimitedDataModelElement(self.id_, b"this is a match context.\n")
        match_element = delimited_data_model_element.get_match_element(self.path, match_context)
        self.compare_no_match_results(data, match_element, match_context)

    def test7special_characters_escape(self):
        """In this test case special character escaping is tested. The delimiter is not consumed (consume_delimiter=False)."""
        data = b'error: the command \\"python run.py\\" was not found" '
        value = b'error: the command \\"python run.py\\" was not found'
        match_context = DummyMatchContext(data)
        delimited_data_model_element = DelimitedDataModelElement(self.id_, b'"', b"\\")
        match_element = delimited_data_model_element.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, value, value, None)

        data = rb"^This is a simple regex string. It costs 10\$.$"
        value = rb"^This is a simple regex string. It costs 10\$."
        match_context = DummyMatchContext(data)
        delimited_data_model_element = DelimitedDataModelElement(self.id_, b"$", b"\\")
        match_element = delimited_data_model_element.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, value, value, None)

        data = b"the searched file is .gitignore."
        value = b"the searched file is .gitignore"
        match_context = DummyMatchContext(data)
        delimited_data_model_element = DelimitedDataModelElement(self.id_, b".", b" ")
        match_element = delimited_data_model_element.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, value, value, None)

    def test8special_characters_escape_no_match(self):
        """In this test case special character escaping is tested without matching."""
        data = b'error: the command \\"python run.py\\" was not found\\" '
        match_context = DummyMatchContext(data)
        delimited_data_model_element = DelimitedDataModelElement(self.id_, b'"', b"\\")
        match_element = delimited_data_model_element.get_match_element(self.path, match_context)
        self.compare_no_match_results(data, match_element, match_context)

        data = rb"^This is a simple regex string. It costs 10\$.\$"
        match_context = DummyMatchContext(data)
        delimited_data_model_element = DelimitedDataModelElement(self.id_, b"$", b"\\")
        match_element = delimited_data_model_element.get_match_element(self.path, match_context)
        self.compare_no_match_results(data, match_element, match_context)

        data = b"the searched file is .gitignore ."
        match_context = DummyMatchContext(data)
        delimited_data_model_element = DelimitedDataModelElement(self.id_, b".", b" ")
        match_element = delimited_data_model_element.get_match_element(self.path, match_context)
        self.compare_no_match_results(data, match_element, match_context)

    def test9consume_delimiter(self):
        """In this test case check if the consume_delimiter parameter is working properly."""
        data = b"this is a match context.\n"

        delimited_data_model_element = DelimitedDataModelElement(self.id_, b"a", consume_delimiter=True)
        value = b"this is a"
        match_context = DummyMatchContext(data)
        match_element = delimited_data_model_element.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, value, value, None)

        delimited_data_model_element = DelimitedDataModelElement(self.id_, b"c", consume_delimiter=True)
        value = b"this is a matc"
        match_context = DummyMatchContext(data)
        match_element = delimited_data_model_element.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, value, value, None)

        delimited_data_model_element = DelimitedDataModelElement(self.id_, b"e", consume_delimiter=True)
        value = b"this is a match conte"
        match_context = DummyMatchContext(data)
        match_element = delimited_data_model_element.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, value, value, None)

        delimited_data_model_element = DelimitedDataModelElement(self.id_, b"\n", consume_delimiter=True)
        value = b"this is a match context.\n"
        match_context = DummyMatchContext(data)
        match_element = delimited_data_model_element.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, value, value, None)

        value = b"this is"
        match_context = DummyMatchContext(data)
        delimited_data_model_element = DelimitedDataModelElement(self.id_, b" is", consume_delimiter=True)
        match_element = delimited_data_model_element.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, value, value, None)

        value = b"this"
        match_context = DummyMatchContext(data)
        delimited_data_model_element = DelimitedDataModelElement(self.id_, b"is", consume_delimiter=True)
        match_element = delimited_data_model_element.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, value, value, None)

        value = b"this is a match context.\n"
        match_context = DummyMatchContext(data)
        delimited_data_model_element = DelimitedDataModelElement(self.id_, b"context.\n", consume_delimiter=True)
        match_element = delimited_data_model_element.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, value, value, None)

        value = b"this is a match context.\n"
        match_context = DummyMatchContext(data)
        delimited_data_model_element = DelimitedDataModelElement(self.id_, b"his is a match context.\n", consume_delimiter=True)
        match_element = delimited_data_model_element.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, value, value, None)

    def test10consume_delimiter_no_match(self):
        """In this test case check if the consume_delimiter parameter is working properly and does not match data."""
        data = b"this is a match context.\n"

        for char in "bdfgjklpqruvwyz":
            delimited_data_model_element = DelimitedDataModelElement(self.id_, char.encode(), consume_delimiter=True)
            match_context = DummyMatchContext(data)
            match_element = delimited_data_model_element.get_match_element(self.path, match_context)
            self.compare_no_match_results(data, match_element, match_context)

        match_context = DummyMatchContext(data)
        delimited_data_model_element = DelimitedDataModelElement(self.id_, b"other data", consume_delimiter=True)
        match_element = delimited_data_model_element.get_match_element(self.path, match_context)
        self.compare_no_match_results(data, match_element, match_context)

        match_context = DummyMatchContext(data)
        delimited_data_model_element = DelimitedDataModelElement(self.id_, b"isa", consume_delimiter=True)
        match_element = delimited_data_model_element.get_match_element(self.path, match_context)
        self.compare_no_match_results(data, match_element, match_context)

        match_context = DummyMatchContext(data)
        delimited_data_model_element = DelimitedDataModelElement(self.id_, b"context\n", consume_delimiter=True)
        match_element = delimited_data_model_element.get_match_element(self.path, match_context)
        self.compare_no_match_results(data, match_element, match_context)

        match_context = DummyMatchContext(data)
        delimited_data_model_element = DelimitedDataModelElement(self.id_, b"this is a match context.\n", consume_delimiter=True)
        match_element = delimited_data_model_element.get_match_element(self.path, match_context)
        self.compare_no_match_results(data, match_element, match_context)

    def test11element_id_input_validation(self):
        """Check if element_id is validated."""
        self.assertRaises(ValueError, DelimitedDataModelElement, "", self.delimiter)  # empty element_id
        self.assertRaises(TypeError, DelimitedDataModelElement, None, self.delimiter)  # None element_id
        self.assertRaises(TypeError, DelimitedDataModelElement, b"path", self.delimiter)  # bytes element_id is not allowed
        self.assertRaises(TypeError, DelimitedDataModelElement, True, self.delimiter)  # boolean element_id is not allowed
        self.assertRaises(TypeError, DelimitedDataModelElement, 123, self.delimiter)  # integer element_id is not allowed
        self.assertRaises(TypeError, DelimitedDataModelElement, 123.22, self.delimiter)  # float element_id is not allowed
        self.assertRaises(TypeError, DelimitedDataModelElement, {"id": "path"}, self.delimiter)  # dict element_id is not allowed
        self.assertRaises(TypeError, DelimitedDataModelElement, ["path"], self.delimiter)  # list element_id is not allowed
        self.assertRaises(TypeError, DelimitedDataModelElement, [], self.delimiter)  # empty list element_id is not allowed
        self.assertRaises(TypeError, DelimitedDataModelElement, (), self.delimiter)  # empty tuple element_id is not allowed
        self.assertRaises(TypeError, DelimitedDataModelElement, set(), self.delimiter)  # empty set element_id is not allowed

    def test12escape_input_validation(self):
        """Check if escape is validated."""
        self.assertRaises(ValueError, DelimitedDataModelElement, self.id_, self.delimiter, escape=b"")  # empty escape
        self.assertRaises(TypeError, DelimitedDataModelElement, self.id_, self.delimiter, escape="\\")  # string escape is not allowed
        self.assertRaises(TypeError, DelimitedDataModelElement, self.id_, self.delimiter, escape=True)  # boolean escape is not allowed
        self.assertRaises(TypeError, DelimitedDataModelElement, self.id_, self.delimiter, escape=123)  # integer escape is not allowed
        self.assertRaises(TypeError, DelimitedDataModelElement, self.id_, self.delimiter, escape=123.22)  # float escape is not allowed
        self.assertRaises(TypeError, DelimitedDataModelElement, self.id_, self.delimiter, escape={"id": "path"})  # dict escape not allowed
        self.assertRaises(TypeError, DelimitedDataModelElement, self.id_, self.delimiter, escape=["path"])  # list escape is not allowed
        self.assertRaises(TypeError, DelimitedDataModelElement, self.id_, self.delimiter, escape=[])  # empty list escape is not allowed
        self.assertRaises(TypeError, DelimitedDataModelElement, self.id_, self.delimiter, escape=())  # empty tuple escape is not allowed
        self.assertRaises(TypeError, DelimitedDataModelElement, self.id_, self.delimiter, escape=set())  # empty set escape is not allowed

    def test13consume_delimiter_input_validation(self):
        """Check if consume_delimiter is validated."""
        self.assertRaises(TypeError, DelimitedDataModelElement, self.id_, self.delimiter, consume_delimiter=b"")
        self.assertRaises(TypeError, DelimitedDataModelElement, self.id_, self.delimiter, consume_delimiter="\\")
        self.assertRaises(TypeError, DelimitedDataModelElement, self.id_, self.delimiter, consume_delimiter=123)
        self.assertRaises(TypeError, DelimitedDataModelElement, self.id_, self.delimiter, consume_delimiter=123.22)
        self.assertRaises(TypeError, DelimitedDataModelElement, self.id_, self.delimiter, consume_delimiter={"id": "path"})
        self.assertRaises(TypeError, DelimitedDataModelElement, self.id_, self.delimiter, consume_delimiter=["path"])
        self.assertRaises(TypeError, DelimitedDataModelElement, self.id_, self.delimiter, consume_delimiter=[])
        self.assertRaises(TypeError, DelimitedDataModelElement, self.id_, self.delimiter, consume_delimiter=())
        self.assertRaises(TypeError, DelimitedDataModelElement, self.id_, self.delimiter, consume_delimiter=set())

    def test14get_match_element_match_context_input_validation(self):
        """Check if an exception is raised, when other classes than MatchContext are used in get_match_element."""
        model_element = DelimitedDataModelElement(self.id_, self.delimiter)
        data = b"one, two, three"
        model_element.get_match_element(self.path, DummyMatchContext(data))
        model_element.get_match_element(self.path, MatchContext(data))

        self.assertRaises(AttributeError, model_element.get_match_element, self.path, MatchElement(None, data, None, None))
        self.assertRaises(AttributeError, model_element.get_match_element, self.path, data)
        self.assertRaises(AttributeError, model_element.get_match_element, self.path, data.decode())
        self.assertRaises(AttributeError, model_element.get_match_element, self.path, True)
        self.assertRaises(AttributeError, model_element.get_match_element, self.path, 123)
        self.assertRaises(AttributeError, model_element.get_match_element, self.path, 123.22)
        self.assertRaises(AttributeError, model_element.get_match_element, self.path, None)
        self.assertRaises(AttributeError, model_element.get_match_element, self.path, [])
        self.assertRaises(AttributeError, model_element.get_match_element, self.path, {"key": MatchContext(data)})
        self.assertRaises(AttributeError, model_element.get_match_element, self.path, set())
        self.assertRaises(AttributeError, model_element.get_match_element, self.path, ())
        self.assertRaises(AttributeError, model_element.get_match_element, self.path, model_element)

    def test5consume_delimeter(self):
        """In this test case check if the consume_delimeter parameter is working properly."""
        match_context = MatchContext(self.match_context_string)
        delimited_data_model_element = DelimitedDataModelElement('id', b'c', consume_delimiter=False)
        match_element = delimited_data_model_element.get_match_element('match', match_context)
        self.assertEqual(match_element.get_match_string(), b'this is a mat')

        match_context = MatchContext(self.match_context_string)
        delimited_data_model_element = DelimitedDataModelElement('id', b'c', consume_delimiter=True)
        match_element = delimited_data_model_element.get_match_element('match', match_context)
        self.assertEqual(match_element.get_match_string(), b'this is a matc')

        match_context = MatchContext(self.match_context_string)
        delimited_data_model_element = DelimitedDataModelElement('id', b' is', consume_delimiter=False)
        match_element = delimited_data_model_element.get_match_element('match', match_context)
        self.assertEqual(match_element.get_match_string(), b'this')

        match_context = MatchContext(self.match_context_string)
        delimited_data_model_element = DelimitedDataModelElement('id', b' is', consume_delimiter=True)
        match_element = delimited_data_model_element.get_match_element('match', match_context)
        self.assertEqual(match_element.get_match_string(), b'this is')


if __name__ == "__main__":
    unittest.main()
