import unittest
from aminer.parsing.DelimitedDataModelElement import DelimitedDataModelElement
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
        # empty element_id
        element_id = ""
        self.assertRaises(ValueError, DelimitedDataModelElement, element_id, self.delimiter)

        # None element_id
        element_id = None
        self.assertRaises(TypeError, DelimitedDataModelElement, element_id, self.delimiter)

        # bytes element_id is not allowed
        element_id = b"path"
        self.assertRaises(TypeError, DelimitedDataModelElement, element_id, self.delimiter)

        # boolean element_id is not allowed
        element_id = True
        self.assertRaises(TypeError, DelimitedDataModelElement, element_id, self.delimiter)

        # integer element_id is not allowed
        element_id = 123
        self.assertRaises(TypeError, DelimitedDataModelElement, element_id, self.delimiter)

        # float element_id is not allowed
        element_id = 123.22
        self.assertRaises(TypeError, DelimitedDataModelElement, element_id, self.delimiter)

        # dict element_id is not allowed
        element_id = {"id": "path"}
        self.assertRaises(TypeError, DelimitedDataModelElement, element_id, self.delimiter)

        # list element_id is not allowed
        element_id = ["path"]
        self.assertRaises(TypeError, DelimitedDataModelElement, element_id, self.delimiter)

        # empty list element_id is not allowed
        element_id = []
        self.assertRaises(TypeError, DelimitedDataModelElement, element_id, self.delimiter)

        # empty tuple element_id is not allowed
        element_id = ()
        self.assertRaises(TypeError, DelimitedDataModelElement, element_id, self.delimiter)

        # empty set element_id is not allowed
        element_id = set()
        self.assertRaises(TypeError, DelimitedDataModelElement, element_id, self.delimiter)

    def test12escape_input_validation(self):
        """Check if escape is validated."""
        # empty escape
        escape = b""
        self.assertRaises(ValueError, DelimitedDataModelElement, self.id_, self.delimiter, escape=escape)

        # string escape is not allowed
        escape = "\\"
        self.assertRaises(TypeError, DelimitedDataModelElement, self.id_, self.delimiter, escape=escape)

        # boolean escape is not allowed
        escape = True
        self.assertRaises(TypeError, DelimitedDataModelElement, self.id_, self.delimiter, escape=escape)

        # integer escape is not allowed
        escape = 123
        self.assertRaises(TypeError, DelimitedDataModelElement, self.id_, self.delimiter, escape=escape)

        # float escape is not allowed
        escape = 123.22
        self.assertRaises(TypeError, DelimitedDataModelElement, self.id_, self.delimiter, escape=escape)

        # dict escape is not allowed
        escape = {"id": "path"}
        self.assertRaises(TypeError, DelimitedDataModelElement, self.id_, self.delimiter, escape=escape)

        # list escape is not allowed
        escape = ["path"]
        self.assertRaises(TypeError, DelimitedDataModelElement, self.id_, self.delimiter, escape=escape)

        # empty list escape is not allowed
        escape = []
        self.assertRaises(TypeError, DelimitedDataModelElement, self.id_, self.delimiter, escape=escape)

        # empty tuple escape is not allowed
        escape = ()
        self.assertRaises(TypeError, DelimitedDataModelElement, self.id_, self.delimiter, escape=escape)

        # empty set escape is not allowed
        escape = set()
        self.assertRaises(TypeError, DelimitedDataModelElement, self.id_, self.delimiter, escape=escape)

    def test13consume_delimiter_input_validation(self):
        """Check if consume_delimiter is validated."""
        # bytes consume_delimiter is not allowed
        consume_delimiter = b""
        self.assertRaises(TypeError, DelimitedDataModelElement, self.id_, self.delimiter, consume_delimiter=consume_delimiter)

        # string consume_delimiter is not allowed
        consume_delimiter = "\\"
        self.assertRaises(TypeError, DelimitedDataModelElement, self.id_, self.delimiter, consume_delimiter=consume_delimiter)

        # integer consume_delimiter is not allowed
        consume_delimiter = 123
        self.assertRaises(TypeError, DelimitedDataModelElement, self.id_, self.delimiter, consume_delimiter=consume_delimiter)

        # float consume_delimiter is not allowed
        consume_delimiter = 123.22
        self.assertRaises(TypeError, DelimitedDataModelElement, self.id_, self.delimiter, consume_delimiter=consume_delimiter)

        # dict consume_delimiter is not allowed
        consume_delimiter = {"id": "path"}
        self.assertRaises(TypeError, DelimitedDataModelElement, self.id_, self.delimiter, consume_delimiter=consume_delimiter)

        # list consume_delimiter is not allowed
        consume_delimiter = ["path"]
        self.assertRaises(TypeError, DelimitedDataModelElement, self.id_, self.delimiter, consume_delimiter=consume_delimiter)

        # empty list consume_delimiter is not allowed
        consume_delimiter = []
        self.assertRaises(TypeError, DelimitedDataModelElement, self.id_, self.delimiter, consume_delimiter=consume_delimiter)

        # empty tuple consume_delimiter is not allowed
        consume_delimiter = ()
        self.assertRaises(TypeError, DelimitedDataModelElement, self.id_, self.delimiter, consume_delimiter=consume_delimiter)

        # empty set consume_delimiter is not allowed
        consume_delimiter = set()
        self.assertRaises(TypeError, DelimitedDataModelElement, self.id_, self.delimiter, consume_delimiter=consume_delimiter)

    def test14get_match_element_match_context_input_validation(self):
        """Check if an exception is raised, when other classes than MatchContext are used in get_match_element."""
        model_element = DelimitedDataModelElement(self.id_, self.delimiter)
        data = b"one, two, three"
        model_element.get_match_element(self.path, DummyMatchContext(data))
        from aminer.parsing.MatchContext import MatchContext
        model_element.get_match_element(self.path, MatchContext(data))

        from aminer.parsing.MatchElement import MatchElement
        self.assertRaises(AttributeError, model_element.get_match_element, self.path, MatchElement(data, None, None, None))
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


if __name__ == "__main__":
    unittest.main()
