import copy
import unittest
import json
from aminer.parsing.JsonModelElement import JsonModelElement
from aminer.parsing.MatchContext import MatchContext
from aminer.parsing.MatchElement import MatchElement
from aminer.parsing.DecimalFloatValueModelElement import DecimalFloatValueModelElement
from unit.TestBase import TestBase, DummyMatchContext, DummyFixedDataModelElement, DummyFirstMatchModelElement


class JsonModelElementTest(TestBase):
    """Unittests for the JsonModelElement."""

    id_ = "json"
    path = "path"
    single_line_json = b'{"menu": {"id": "file", "value": "File", "popup": {"menuitem": [{"value": "New", "onclick": "CreateNewDoc()"}, {' \
                       b'"value": "Open", "onclick": "OpenDoc()"}, {"value": "Close", "onclick": "CloseDoc()"}, ' \
                       b'{"value": "Undo", "onclick": "UndoDoc()", "clickable": true}]}}}'
    single_line_with_optional_key_json = b'{"menu": {"id": "file", "value": "File", "popup": {"menuitem": [{"value": "New", "onclick":' \
                                         b' "CreateNewDoc()", "clickable": false}, {"value": "Open", "onclick": "OpenDoc()"}, {"value": ' \
                                         b'"Close", "onclick": "CloseDoc()", "clickable": false}]}}}'
    single_line_missing_key_json = b'{"menu": {"id": "file", "popup": {"menuitem": [{"value": "New", "onclick": "CreateNewDoc()"}, {' \
                                   b'"value": "Open", "onclick": "OpenDoc()"}, {"value": "Close", "onclick": "CloseDoc()"}]}}}'
    single_line_object_instead_of_array = b'{"menu": {"id": "file", "popup": {"menuitem": {"value": "New", "onclick": "CreateNewDoc()"}}}}'
    single_line_invalid_json = b'{"menu": {"id": "file", "value": "File", "popup": {"menuitem": [{"value": "New", "onclick": "CreateNew' \
                               b'Doc()"}, {"value": "Open", "onclick": "OpenDoc()"}, {"value": "Close", "onclick": "CloseDoc()"'
    single_line_no_match_json = b'{"menu": {"id": "NoMatch", "value": "File", "popup": {"menuitem": [{"value": "New", "onclick": "Create' \
                                b'NewDoc()"}, {"value": "Open", "onclick": "OpenDoc()"}, {"value": "Close", "onclick": "CloseDoc()"}]}}}'
    single_line_different_order_with_optional_key_json = \
        b'{"menu": {"value": "File","popup": {"menuitem": [{"clickable": false, "value": "New", "onclick": "CreateNewDoc()"}, {' \
        b'"onclick": "OpenDoc()", "value": "Open"}, {"value": "Close", "onclick": "CloseDoc()", "clickable": false}]}, "id": "file"}}'
    single_line_json_array = b'{"menu": {"id": "file", "value": "File", "popup": ["value", "value", "value"]}}'
    single_line_escaped_json = br'{"a": "\x2d"}'
    single_line_empty_array = b'{"menu": {"id": "file", "value": "File", "popup": {"menuitem": []}}}'
    single_line_multiple_menuitems = \
        b'{"menu": {"id": "file", "value": "File", "popup": {"menuitem": [{"value": "New", "onclick": "CreateNewDoc()"}, {"value": ' \
        b'"Open", "onclick": "OpenDoc()"}, {"value": "Close", "onclick": "CloseDoc()"}, , ]}}}'
    multi_line_json = b"""{
  "menu": {
    "id": "file",
    "value": "File",
    "popup": {
      "menuitem": [
        {"value": "New", "onclick": "CreateNewDoc()"},
        {"value": "Open", "onclick": "OpenDoc()"},
        {"value": "Close", "onclick": "CloseDoc()"}
      ]
    }
  }
}"""
    everything_new_line_json = b"""{
  "menu":
  {
    "id": "file",
    "value": "File",
    "popup":
    {
      "menuitem":
      [
        {
          "value": "New",
          "onclick": "CreateNewDoc()"
        },
        {
          "value": "Open",
          "onclick": "OpenDoc()"
        },
        {
          "value": "Close",
          "onclick": "CloseDoc()"
        }
      ]
    }
  }
}"""
    array_of_arrays = b'{"a": [["abc", "abc", "abc"], ["abc", "abc"], ["abc"]]}'
    key_parser_dict = {"menu": {
        "id": DummyFixedDataModelElement("id", b"file"),
        "value": DummyFixedDataModelElement("value", b"File"),
        "popup": {
            "menuitem": [{
                "value": DummyFirstMatchModelElement("buttonNames", [
                    DummyFixedDataModelElement("new", b"New"), DummyFixedDataModelElement("open", b"Open"),
                    DummyFixedDataModelElement("close", b"Close")]),
                "onclick": DummyFirstMatchModelElement("buttonOnclick", [
                    DummyFixedDataModelElement("create_new_doc", b"CreateNewDoc()"),
                    DummyFixedDataModelElement("open_doc", b"OpenDoc()"), DummyFixedDataModelElement("close_doc", b"CloseDoc()")]),
                "optional_key_clickable": DummyFirstMatchModelElement("clickable", [
                    DummyFixedDataModelElement("true", b"true"), DummyFixedDataModelElement("false", b"false")])
            }, {
                "value": DummyFirstMatchModelElement("buttonNames", [DummyFixedDataModelElement("undo", b"Undo")]),
                "onclick": DummyFirstMatchModelElement("buttonOnclick", [DummyFixedDataModelElement("undo_doc", b"UndoDoc()")]),
                "clickable": DummyFirstMatchModelElement("clickable", [
                    DummyFixedDataModelElement("true", b"true"), DummyFixedDataModelElement("false", b"false")])
            }]
        }}}
    key_parser_dict_allow_all = {"menu": {
        "id": DummyFixedDataModelElement("id", b"file"),
        "value": DummyFixedDataModelElement("value", b"File"),
        "popup": "ALLOW_ALL"
    }}
    key_parser_dict_array = {"menu": {
        "id": DummyFixedDataModelElement("id", b"file"),
        "value": DummyFixedDataModelElement("value", b"File"),
        "popup": [
            DummyFixedDataModelElement("value", b"value")
        ]
    }}
    key_parser_dict_escaped = {"a":  DummyFixedDataModelElement("id", b"-")}
    empty_key_parser_dict = {"optional_key_key": DummyFixedDataModelElement("key", b"value")}
    key_parser_dict_allow_all_fields = {"menu": {
        "id": DummyFixedDataModelElement("id", b"file")
    }}
    key_parser_dict_array_of_arrays = {"a": [[DummyFixedDataModelElement("abc", b"abc")]]}

    def test1get_id(self):
        """Test if get_id works properly."""
        json_me = JsonModelElement(self.id_, self.key_parser_dict)
        self.assertEqual(json_me.get_id(), self.id_)

    def test2get_child_elements(self):
        """Test if get_child_elements returns None."""
        k = self.key_parser_dict
        json_me = JsonModelElement(self.id_, self.key_parser_dict)
        self.assertEqual(json_me.get_child_elements(), [
            k["menu"]["id"], k["menu"]["value"], [
                k["menu"]["popup"]["menuitem"][0]["value"], k["menu"]["popup"]["menuitem"][0]["onclick"],
                k["menu"]["popup"]["menuitem"][0]["optional_key_clickable"], k["menu"]["popup"]["menuitem"][1]["value"],
                k["menu"]["popup"]["menuitem"][1]["onclick"], k["menu"]["popup"]["menuitem"][1]["clickable"]]])

    def test3get_match_element_valid_match(self):
        """Parse matching substring from MatchContext and check if the MatchContext was updated with all characters."""
        json_model_element = JsonModelElement(self.id_, self.key_parser_dict)
        data = self.single_line_json
        value = json.loads(data)
        match_context = DummyMatchContext(data)
        match_element = json_model_element.get_match_element(self.path, match_context)
        match_context.match_string = str(json.loads(match_context.match_string)).encode()
        self.compare_match_results(
            data, match_element, match_context, self.id_, self.path, str(value).encode(), value, match_element.children)

        data = self.multi_line_json
        value = json.loads(data)
        match_context = DummyMatchContext(data)
        match_element = json_model_element.get_match_element(self.path, match_context)
        match_context.match_string = str(json.loads(match_context.match_string)).encode()
        match_context.match_data = data[len(match_context.match_string):]
        self.compare_match_results(
            data, match_element, match_context, self.id_, self.path, str(value).encode(), value, match_element.children)

        data = self.everything_new_line_json
        value = json.loads(data)
        match_context = DummyMatchContext(data)
        match_element = json_model_element.get_match_element(self.path, match_context)
        match_context.match_string = str(json.loads(match_context.match_string)).encode()
        match_context.match_data = data[len(match_context.match_string):]
        self.compare_match_results(
            data, match_element, match_context, self.id_, self.path, str(value).encode(), value, match_element.children)

        # Test if keys differently ordered than in the key_parser_dict are parsed properly.
        data = self.single_line_different_order_with_optional_key_json
        value = json.loads(data)
        match_context = DummyMatchContext(data)
        match_element = json_model_element.get_match_element(self.path, match_context)
        match_context.match_string = str(json.loads(match_context.match_string)).encode()
        match_context.match_data = data[len(match_context.match_string):]
        self.compare_match_results(
            data, match_element, match_context, self.id_, self.path, str(value).encode(), value, match_element.children)

        data = self.single_line_empty_array
        value = json.loads(data)
        match_context = DummyMatchContext(data)
        match_element = json_model_element.get_match_element(self.path, match_context)
        match_context.match_string = str(json.loads(match_context.match_string)).encode()
        match_context.match_data = data[len(match_context.match_string):]
        self.compare_match_results(
            data, match_element, match_context, self.id_, self.path, str(value).encode(), value, match_element.children)

        json_model_element = JsonModelElement(self.id_, self.key_parser_dict_allow_all)
        data = self.single_line_different_order_with_optional_key_json
        value = json.loads(data)
        match_context = DummyMatchContext(data)
        match_element = json_model_element.get_match_element(self.path, match_context)
        match_context.match_string = str(value).encode()
        match_context.match_data = data[len(match_context.match_string):]
        self.compare_match_results(
            data, match_element, match_context, self.id_, self.path, str(value).encode(), value, match_element.children)

        json_model_element = JsonModelElement(self.id_, self.key_parser_dict_array)
        data = self.single_line_json_array
        value = json.loads(data)
        match_context = DummyMatchContext(data)
        match_element = json_model_element.get_match_element(self.path, match_context)
        match_context.match_string = str(value).encode()
        match_context.match_data = data[len(match_context.match_string):]
        self.compare_match_results(
            data, match_element, match_context, self.id_, self.path, str(value).encode(), value, match_element.children)

        json_model_element = JsonModelElement(self.id_, self.key_parser_dict_escaped)
        data = self.single_line_escaped_json.decode("unicode-escape").encode()
        value = json.loads(data)
        match_context = DummyMatchContext(data)
        match_element = json_model_element.get_match_element(self.path, match_context)
        match_context.match_string = str(value).encode()
        match_context.match_data = data[len(match_context.match_string):]
        self.compare_match_results(
            data, match_element, match_context, self.id_, self.path, str(value).encode(), value, match_element.children)

        json_model_element = JsonModelElement(self.id_, self.key_parser_dict_array_of_arrays)
        data = self.array_of_arrays
        value = json.loads(data)
        match_context = DummyMatchContext(data)
        match_element = json_model_element.get_match_element(self.path, match_context)
        match_context.match_string = str(json.loads(match_context.match_string)).encode()
        self.compare_match_results(
            data, match_element, match_context, self.id_, self.path, str(value).encode(), value, match_element.children)

    def test4get_match_element_with_optional_key(self):
        """Validate optional keys with the optional_key_prefix."""
        json_model_element = JsonModelElement(self.id_, self.key_parser_dict)
        data = self.single_line_with_optional_key_json
        value = json.loads(data)
        match_context = DummyMatchContext(data)
        match_element = json_model_element.get_match_element(self.path, match_context)
        match_context.match_string = str(json.loads(match_context.match_string)).encode()
        match_context.match_data = data[len(match_context.match_string):]
        self.compare_match_results(
            data, match_element, match_context, self.id_, self.path, str(value).encode(), value, match_element.children)

        json_model_element = JsonModelElement(self.id_, self.empty_key_parser_dict)
        data = b"{}"
        value = json.loads(data)
        match_context = DummyMatchContext(data)
        match_element = json_model_element.get_match_element(self.path, match_context)
        match_context.match_string = str(json.loads(data)).encode()
        match_context.match_data = data[len(match_context.match_string):]
        self.compare_match_results(
            data, match_element, match_context, self.id_, self.path, str(value).encode(), value, match_element.children)

    def test5get_match_element_with_allow_all(self):
        """Test a simplified key_parser_dict with ALLOW_ALL."""
        json_model_element = JsonModelElement(self.id_, self.key_parser_dict_allow_all)
        data = self.single_line_json
        value = json.loads(data)
        match_context = DummyMatchContext(data)
        match_element = json_model_element.get_match_element(self.path, match_context)
        match_context.match_string = str(value).encode()
        match_context.match_data = data[len(match_context.match_string):]
        self.compare_match_results(
            data, match_element, match_context, self.id_, self.path, str(value).encode(), value, match_element.children)

        data = self.multi_line_json
        value = json.loads(data)
        match_context = DummyMatchContext(data)
        match_element = json_model_element.get_match_element(self.path, match_context)
        match_context.match_string = str(value).encode()
        match_context.match_data = data[len(match_context.match_string):]
        self.compare_match_results(
            data, match_element, match_context, self.id_, self.path, str(value).encode(), value, match_element.children)

        data = self.everything_new_line_json
        value = json.loads(data)
        match_context = DummyMatchContext(data)
        match_element = json_model_element.get_match_element(self.path, match_context)
        match_context.match_string = str(value).encode()
        match_context.match_data = data[len(match_context.match_string):]
        self.compare_match_results(
            data, match_element, match_context, self.id_, self.path, str(value).encode(), value, match_element.children)

    def test6get_match_element_null_value(self):
        """Test if null values are parsed to "null"."""
        key_parser_dict = {
            "works": DummyFirstMatchModelElement("id", [
                DummyFixedDataModelElement("abc", b"abc"), DummyFixedDataModelElement("123", b"123")]),
            "null": DummyFirstMatchModelElement("wordlist", [
                DummyFixedDataModelElement("allowed", b"allowed value"), DummyFixedDataModelElement("problem", b"null")])}
        data1 = b"""{
            "works": "abc",
            "null": "allowed value"
        }"""
        data2 = b"""{
            "works": "123",
            "null": null
        }"""
        json_model_element = JsonModelElement(self.id_, key_parser_dict)
        data = data1
        value = json.loads(data)
        match_context = DummyMatchContext(data)
        match_element = json_model_element.get_match_element(self.path, match_context)
        match_context.match_string = str(value).encode()
        match_context.match_data = data[len(match_context.match_string):]
        self.compare_match_results(
            data, match_element, match_context, self.id_, self.path, str(value).encode(), value, match_element.children)

        data = data2
        value = json.loads(data)
        match_context = DummyMatchContext(data)
        match_element = json_model_element.get_match_element(self.path, match_context)
        match_context.match_string = str(value).encode()
        match_context.match_data = data[len(match_context.match_string):]
        self.compare_match_results(
            data, match_element, match_context, self.id_, self.path, str(value).encode(), value, match_element.children)

    def test7get_match_element_with_umlaut(self):
        """Test if ä ö ü are used correctly."""
        key_parser_dict = {"works": DummyFixedDataModelElement("abc", "a ä ü ö z".encode("utf-8"))}
        data = """{
            "works": "a ä ü ö z"
        }""".encode("utf-8")
        json_model_element = JsonModelElement(self.id_, key_parser_dict)
        value = json.loads(data)
        match_context = DummyMatchContext(data)
        match_element = json_model_element.get_match_element(self.path, match_context)
        match_context.match_string = str(value).encode()
        match_context.match_data = data[len(match_context.match_string):]
        self.compare_match_results(
            data, match_element, match_context, self.id_, self.path, str(value).encode(), value, match_element.children)

    def test8get_match_element_same_value_as_key(self):
        """Test if object with the same key-value pairs are parsed correctly."""
        key_parser_dict = {"abc": DummyFirstMatchModelElement("first", [
            DummyFixedDataModelElement("abc", b"abc"), DummyFixedDataModelElement("abc", b"ab"), DummyFixedDataModelElement("abc", b"bc"),
            DummyFixedDataModelElement("abc", b"ba"), DummyFixedDataModelElement("abc", b"b"), DummyFixedDataModelElement("abc", b"d")])}
        data = b"""{"abc":"abc"}"""
        json_model_element = JsonModelElement(self.id_, key_parser_dict)
        value = json.loads(data)
        match_context = DummyMatchContext(data)
        match_element = json_model_element.get_match_element(self.path, match_context)
        match_context.match_string = str(value).encode()
        match_context.match_data = data[len(match_context.match_string):]
        self.compare_match_results(
            data, match_element, match_context, self.id_, self.path, str(value).encode(), value, match_element.children)

        data = b"""{"abc":"ab"}"""
        json_model_element = JsonModelElement(self.id_, key_parser_dict)
        value = json.loads(data)
        match_context = DummyMatchContext(data)
        match_element = json_model_element.get_match_element(self.path, match_context)
        match_context.match_string = str(value).encode()
        match_context.match_data = data[len(match_context.match_string):]
        self.compare_match_results(
            data, match_element, match_context, self.id_, self.path, str(value).encode(), value, match_element.children)

        data = b"""{"abc":"bc"}"""
        json_model_element = JsonModelElement(self.id_, key_parser_dict)
        value = json.loads(data)
        match_context = DummyMatchContext(data)
        match_element = json_model_element.get_match_element(self.path, match_context)
        match_context.match_string = str(value).encode()
        match_context.match_data = data[len(match_context.match_string):]
        self.compare_match_results(
            data, match_element, match_context, self.id_, self.path, str(value).encode(), value, match_element.children)

        data = b"""{"abc":"b"}"""
        json_model_element = JsonModelElement(self.id_, key_parser_dict)
        value = json.loads(data)
        match_context = DummyMatchContext(data)
        match_element = json_model_element.get_match_element(self.path, match_context)
        match_context.match_string = str(value).encode()
        match_context.match_data = data[len(match_context.match_string):]
        self.compare_match_results(
            data, match_element, match_context, self.id_, self.path, str(value).encode(), value, match_element.children)

        data = b"""{"abc":"d"}"""
        json_model_element = JsonModelElement(self.id_, key_parser_dict)
        value = json.loads(data)
        match_context = DummyMatchContext(data)
        match_element = json_model_element.get_match_element(self.path, match_context)
        match_context.match_string = str(value).encode()
        match_context.match_data = data[len(match_context.match_string):]
        self.compare_match_results(
            data, match_element, match_context, self.id_, self.path, str(value).encode(), value, match_element.children)

        data = b"""{"abc":"ba"}"""
        json_model_element = JsonModelElement(self.id_, key_parser_dict)
        value = json.loads(data)
        match_context = DummyMatchContext(data)
        match_element = json_model_element.get_match_element(self.path, match_context)
        match_context.match_string = str(value).encode()
        match_context.match_data = data[len(match_context.match_string):]
        self.compare_match_results(
            data, match_element, match_context, self.id_, self.path, str(value).encode(), value, match_element.children)

    def test9get_match_element_empty_array_empty_object_null(self):
        """Test if the keywords EMPTY_ARRAY, EMPTY_OBJECT, EMPTY_STRING,  and None (null) work properly."""
        key_parser_dict = {"menu": {
            "id": "EMPTY_OBJECT",
            "value": "EMPTY_ARRAY",
            "popup": {
                "menuitem": [{
                    "value": DummyFixedDataModelElement("null", b"null"),
                    "onclick": DummyFirstMatchModelElement("buttonOnclick", [
                        DummyFixedDataModelElement("create_new_doc", b"CreateNewDoc()"),
                        DummyFixedDataModelElement("open_doc", b"OpenDoc()"), DummyFixedDataModelElement("close_doc", b"CloseDoc()")]),
                    "optional_key_clickable": DummyFirstMatchModelElement("clickable", [
                        DummyFixedDataModelElement("true", b"true"), DummyFixedDataModelElement("false", b"false")])
                }]
            }},
            "a": "EMPTY_ARRAY",
            "b": "EMPTY_OBJECT",
            "c": "EMPTY_STRING"
        }
        json_model_element = JsonModelElement(self.id_, key_parser_dict)
        data = b'{"menu": {"id": {}, "value": [], "popup": {"menuitem": [{"value": null, "onclick": "CreateNewDoc()"}, {"value": null, ' \
               b'"onclick": "OpenDoc()"}, {"value": null, "onclick": "CloseDoc()"}]}}, "a": [], "b": {}, "c": ""}'
        value = json.loads(data)
        match_context = DummyMatchContext(data)
        match_element = json_model_element.get_match_element(self.path, match_context)
        match_context.match_string = str(json.loads(match_context.match_string)).encode()
        self.compare_match_results(
            data, match_element, match_context, self.id_, self.path, str(value).encode(), value, match_element.children)

        data = b'{"menu": {"id": {\n}, "value": [\n], "popup": {"menuitem": [{"value": null, "onclick": "CreateNewDoc()"}, {"value": ' \
               b'null, "onclick": "OpenDoc()"}, {"value": null, "onclick": "CloseDoc()"}]}}, "a": [], "b": {}, "c": ""}'
        value = json.loads(data)
        match_context = DummyMatchContext(data)
        match_element = json_model_element.get_match_element(self.path, match_context)
        match_context.match_string = str(json.loads(match_context.match_string)).encode()
        match_context.match_data = data[len(match_context.match_string):]
        self.compare_match_results(
            data, match_element, match_context, self.id_, self.path, str(value).encode(), value, match_element.children)

        data = b'{"menu": {"id": {}, "value": [], "popup": {"menuitem": []}}, "a": [], "b": {}, "c": ""}'
        value = json.loads(data)
        match_context = DummyMatchContext(data)
        match_element = json_model_element.get_match_element(self.path, match_context)
        match_context.match_string = str(json.loads(match_context.match_string)).encode()
        match_context.match_data = data[len(match_context.match_string):]
        self.compare_match_results(
            data, match_element, match_context, self.id_, self.path, str(value).encode(), value, match_element.children)

        JsonModelElement(self.id_, {"a": "EMPTY_ARRAY"})
        JsonModelElement(self.id_, {"a": "EMPTY_OBJECT"})
        JsonModelElement(self.id_, {"a": "EMPTY_STRING"})

        data = b'{"menu": {"id": {}, "value": [], "popup": {"menuitem": [{"value": null, "onclick": "CreateNewDoc()"}, {"value": null, ' \
               b'"onclick": "OpenDoc()"}, {"value": null, "onclick": "CloseDoc()"}]}}, "a": ["a"], "b": {}, "c": ""}'
        match_context = DummyMatchContext(data)
        match_element = json_model_element.get_match_element(self.path, match_context)
        self.compare_no_match_results(data, match_element, match_context)

        data = b'{"menu": {"id": {}, "value": [], "popup": {"menuitem": [{"value": null, "onclick": "CreateNewDoc()"}, {"value": null, ' \
               b'"onclick": "OpenDoc()"}, {"value": null, "onclick": "CloseDoc()"}]}}, "a": [], "b": {"a": "a"}, "c": ""}'
        match_context = DummyMatchContext(data)
        match_element = json_model_element.get_match_element(self.path, match_context)
        self.compare_no_match_results(data, match_element, match_context)

        data = b'{"menu": {"id": {}, "value": [], "popup": {"menuitem": [{"value": null, "onclick": "CreateNewDoc()"}, {"value": null, ' \
               b'"onclick": "OpenDoc()"}, {"value": null, "onclick": "CloseDoc()"}]}}, "a": [], "b": {}, "c": "ab"}'
        match_context = DummyMatchContext(data)
        match_element = json_model_element.get_match_element(self.path, match_context)
        self.compare_no_match_results(data, match_element, match_context)

        data = b'{"menu": {"id": {}, "value": [], "popup": {"menuitem": []}}, "a": [], "b": {}, "c": ""}'
        match_context = DummyMatchContext(data)
        match_element = json_model_element.get_match_element(self.path, match_context)
        self.compare_no_match_results(data, match_element, match_context)

        key_parser_dict = {"ALLOW_ALL_KEYS": DummyFirstMatchModelElement("first", [
            DummyFixedDataModelElement("abc", b"abc"), DummyFixedDataModelElement("123", b"123")])}
        json_model_element = JsonModelElement(self.id_, key_parser_dict)
        data = b'{"key1": "abc", "afd": "abc", "1234": "123", "&544": "123"}'
        value = json.loads(data)
        match_context = DummyMatchContext(data)
        match_element = json_model_element.get_match_element(self.path, match_context)
        match_context.match_string = str(json.loads(match_context.match_string)).encode()
        self.compare_match_results(
            data, match_element, match_context, self.id_, self.path, str(value).encode(), value, match_element.children)

    def test10get_match_element_float_exponents(self):
        """
        Parse float values with exponents.
        The principle of only testing dummy classes can not be applied here, as the functionality between the JsonModelElement and
        DecimalFloatValueModelElement must be tested directly.
        """
        json_model_element = JsonModelElement(self.id_, {
            "a": DecimalFloatValueModelElement(self.id_, exponent_type=DecimalFloatValueModelElement.EXP_TYPE_OPTIONAL),
            "b": DecimalFloatValueModelElement(self.id_, exponent_type=DecimalFloatValueModelElement.EXP_TYPE_OPTIONAL)})

        def format_float(val):
            """
            This function formats the float-value and parses the sign and the exponent
            """
            exp = None
            if "e" in val:
                exp = "e"
            elif "E" in val:
                exp = "E"
            if "+" in val:
                sign = "+"
            else:
                sign = "-"
            if exp is not None:
                pos_point = val.find(exp)
                if "." in val:
                    pos_point = val.find(".")
                if len(val) - val.find(sign) <= 2:
                    result = format(float(val), "1.%dE" % (val.find(exp) - pos_point))[:-2]
                    result += format(float(val), "1.%dE" % (val.find(exp) - pos_point))[-1]
                    return result
                return format(float(val), "1.%dE" % (val.find(exp) - pos_point))
            return float(val)
        data = b'{"a": 111.1, "b": 111.1}'
        value = json.loads(data, parse_float=format_float)
        match_context = DummyMatchContext(data)
        match_element = json_model_element.get_match_element(self.path, match_context)
        match_context.match_string = str(value).encode()
        match_context.match_data = data[len(match_context.match_string):]
        self.compare_match_results(
            data, match_element, match_context, self.id_, self.path, str(value).encode(), value, match_element.children)

        data = b'{"a": 1E-01, "b": 111.1}'
        value = json.loads(data, parse_float=format_float)
        match_context = DummyMatchContext(data)
        match_element = json_model_element.get_match_element(self.path, match_context)
        match_context.match_string = str(value).encode()
        match_context.match_data = data[len(match_context.match_string):]
        self.compare_match_results(
            data, match_element, match_context, self.id_, self.path, str(value).encode(), value, match_element.children)

        data = b'{"a": 111.1, "b": 1E-1}'
        value = json.loads(data, parse_float=format_float)
        match_context = DummyMatchContext(data)
        match_element = json_model_element.get_match_element(self.path, match_context)
        match_context.match_string = str(value).encode()
        match_context.match_data = data[len(match_context.match_string):]
        self.compare_match_results(
            data, match_element, match_context, self.id_, self.path, str(value).encode(), value, match_element.children)

        data = b'{"a": 1E-1, "b": 1E-1}'
        value = json.loads(data, parse_float=format_float)
        match_context = DummyMatchContext(data)
        match_element = json_model_element.get_match_element(self.path, match_context)
        match_context.match_string = str(value).encode()
        match_context.match_data = data[len(match_context.match_string):]
        self.compare_match_results(
            data, match_element, match_context, self.id_, self.path, str(value).encode(), value, match_element.children)

    def test11get_match_element_allow_all_fields(self):
        """Parse matching substring from MatchContext using the allow_all_fields parameter."""
        json_model_element = JsonModelElement(self.id_, self.key_parser_dict_allow_all_fields, allow_all_fields=True)
        data = self.single_line_json
        value = json.loads(data)
        match_context = DummyMatchContext(data)
        match_element = json_model_element.get_match_element(self.path, match_context)
        match_context.match_string = str(json.loads(match_context.match_string)).encode()
        self.compare_match_results(
            data, match_element, match_context, self.id_, self.path, str(value).encode(), value, match_element.children)

        json_model_element = JsonModelElement(self.id_, self.key_parser_dict_allow_all_fields, allow_all_fields=False)
        data = self.single_line_json
        match_context = DummyMatchContext(data)
        match_element = json_model_element.get_match_element(self.path, match_context)
        self.compare_no_match_results(data, match_element, match_context)

    def test12get_match_element_no_match(self):
        """Parse not matching substring from MatchContext and check if the MatchContext was not changed."""
        json_model_element = JsonModelElement(self.id_, self.key_parser_dict)
        # missing key
        data = self.single_line_missing_key_json
        match_context = DummyMatchContext(data)
        match_element = json_model_element.get_match_element(self.path, match_context)
        self.compare_no_match_results(data, match_element, match_context)

        # object instead of array
        data = self.single_line_object_instead_of_array
        match_context = DummyMatchContext(data)
        match_element = json_model_element.get_match_element(self.path, match_context)
        self.compare_no_match_results(data, match_element, match_context)

        # invalid json
        data = self.single_line_invalid_json
        match_context = DummyMatchContext(data)
        match_element = json_model_element.get_match_element(self.path, match_context)
        self.compare_no_match_results(data, match_element, match_context)

        # child not matching
        data = self.single_line_no_match_json
        match_context = DummyMatchContext(data)
        match_element = json_model_element.get_match_element(self.path, match_context)
        self.compare_no_match_results(data, match_element, match_context)

        # all keys missing
        data = b"{}"
        match_context = DummyMatchContext(data)
        match_element = json_model_element.get_match_element(self.path, match_context)
        self.compare_no_match_results(data, match_element, match_context)

        json_model_element = JsonModelElement(self.id_, self.empty_key_parser_dict)
        data = b"[]"
        match_context = DummyMatchContext(data)
        match_element = json_model_element.get_match_element(self.path, match_context)
        self.compare_no_match_results(data, match_element, match_context)

        data = b"{[]}"
        match_context = DummyMatchContext(data)
        match_element = json_model_element.get_match_element(self.path, match_context)
        self.compare_no_match_results(data, match_element, match_context)

        data = b'{"key": []}'
        match_context = DummyMatchContext(data)
        match_element = json_model_element.get_match_element(self.path, match_context)
        self.compare_no_match_results(data, match_element, match_context)

    def test13element_id_input_validation(self):
        """Check if element_id is validated."""
        self.assertRaises(ValueError, JsonModelElement, "", self.key_parser_dict)  # empty element_id
        self.assertRaises(TypeError, JsonModelElement, None, self.key_parser_dict)  # None element_id
        self.assertRaises(TypeError, JsonModelElement, b"path", self.key_parser_dict)  # bytes element_id is not allowed
        self.assertRaises(TypeError, JsonModelElement, True, self.key_parser_dict)  # boolean element_id is not allowed
        self.assertRaises(TypeError, JsonModelElement, 123, self.key_parser_dict)  # integer element_id is not allowed
        self.assertRaises(TypeError, JsonModelElement, 123.22, self.key_parser_dict)  # float element_id is not allowed
        self.assertRaises(TypeError, JsonModelElement, {"id": "path"}, self.key_parser_dict)  # dict element_id is not allowed
        self.assertRaises(TypeError, JsonModelElement, ["path"], self.key_parser_dict)  # list element_id is not allowed
        self.assertRaises(TypeError, JsonModelElement, [], self.key_parser_dict)  # empty list element_id is not allowed
        self.assertRaises(TypeError, JsonModelElement, (), self.key_parser_dict)  # empty tuple element_id is not allowed
        self.assertRaises(TypeError, JsonModelElement, set(), self.key_parser_dict)  # empty set element_id is not allowed

    def test14key_parser_dict_input_validation(self):
        """Check if key_parser_dict is validated."""
        self.assertRaises(TypeError, JsonModelElement, self.id_, "path")  # string key_parser_dict
        self.assertRaises(TypeError, JsonModelElement, self.id_, None)  # None key_parser_dict
        self.assertRaises(TypeError, JsonModelElement, self.id_, b"path")  # bytes key_parser_dict is not allowed
        self.assertRaises(TypeError, JsonModelElement, self.id_, True)  # boolean key_parser_dict is not allowed
        self.assertRaises(TypeError, JsonModelElement, self.id_, 123)  # integer key_parser_dict is not allowed
        self.assertRaises(TypeError, JsonModelElement, self.id_, 123.22)  # float key_parser_dict is not allowed
        # dict key_parser_dict with no ModelElementInterface values is not allowed
        self.assertRaises(TypeError, JsonModelElement, self.id_, {"id": "path"})
        # dict key_parser_dict with list of other lengths than 1 is not allowed.
        key_parser_dict = copy.deepcopy(self.key_parser_dict)
        key_parser_dict["menu"]["popup"]["menuitem"] = []
        self.assertRaises(ValueError, JsonModelElement, self.id_, key_parser_dict)
        self.assertRaises(TypeError, JsonModelElement, self.id_, ["path"])  # list key_parser_dict is not allowed
        self.assertRaises(TypeError, JsonModelElement, self.id_, [])  # empty list key_parser_dict is not allowed
        self.assertRaises(TypeError, JsonModelElement, self.id_, ())  # empty tuple key_parser_dict is not allowed
        self.assertRaises(TypeError, JsonModelElement, self.id_, set())  # empty set key_parser_dict is not allowed

    def test15optional_key_prefix_input_validation(self):
        """Check if optional_key_prefix is validated."""
        self.assertRaises(ValueError, JsonModelElement, self.id_, self.key_parser_dict, "")  # empty optional_key_prefix
        self.assertRaises(TypeError, JsonModelElement, self.id_, self.key_parser_dict, None)  # None optional_key_prefix
        self.assertRaises(TypeError, JsonModelElement, self.id_, self.key_parser_dict, b"path")  # bytes optional_key_prefix is not allowed
        self.assertRaises(TypeError, JsonModelElement, self.id_, self.key_parser_dict, True)  # boolean optional_key_prefix is not allowed
        self.assertRaises(TypeError, JsonModelElement, self.id_, self.key_parser_dict, 123)  # integer optional_key_prefix is not allowed
        self.assertRaises(TypeError, JsonModelElement, self.id_, self.key_parser_dict, 123.22)  # float optional_key_prefix is not allowed
        self.assertRaises(TypeError, JsonModelElement, self.id_, self.key_parser_dict, {"id": "path"})  # dict not allowed
        self.assertRaises(TypeError, JsonModelElement, self.id_, self.key_parser_dict, ["path"])  # list optional_key_prefix is not allowed
        self.assertRaises(TypeError, JsonModelElement, self.id_, self.key_parser_dict, [])  # empty list optional_key_prefix is not allowed
        self.assertRaises(TypeError, JsonModelElement, self.id_, self.key_parser_dict, ())  # empty tuple optional_key_prefix is not allowed
        self.assertRaises(TypeError, JsonModelElement, self.id_, self.key_parser_dict, set())  # empty set optional_key_prefix not allowed

    def test16allow_all_fields_input_validation(self):
        """Check if allow_all_fields is validated."""
        self.assertRaises(TypeError, JsonModelElement, self.id_, self.key_parser_dict, allow_all_fields="")
        self.assertRaises(TypeError, JsonModelElement, self.id_, self.key_parser_dict, allow_all_fields=None)
        self.assertRaises(TypeError, JsonModelElement, self.id_, self.key_parser_dict, allow_all_fields=b"path")
        self.assertRaises(TypeError, JsonModelElement, self.id_, self.key_parser_dict, allow_all_fields=123)
        self.assertRaises(TypeError, JsonModelElement, self.id_, self.key_parser_dict, allow_all_fields=123.22)
        self.assertRaises(TypeError, JsonModelElement, self.id_, self.key_parser_dict, allow_all_fields={"id": "path"})
        self.assertRaises(TypeError, JsonModelElement, self.id_, self.key_parser_dict, allow_all_fields=["path"])
        self.assertRaises(TypeError, JsonModelElement, self.id_, self.key_parser_dict, allow_all_fields=[])
        self.assertRaises(TypeError, JsonModelElement, self.id_, self.key_parser_dict, allow_all_fields=())
        self.assertRaises(TypeError, JsonModelElement, self.id_, self.key_parser_dict, allow_all_fields=set())

    def test17get_match_element_match_context_input_validation(self):
        """Check if an exception is raised, when other classes than MatchContext are used in get_match_element."""
        model_element = JsonModelElement(self.id_, self.key_parser_dict)
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
