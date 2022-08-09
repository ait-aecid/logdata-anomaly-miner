import copy
import unittest
import json
from aminer.parsing.JsonStringModelElement import JsonStringModelElement
from aminer.parsing.MatchContext import MatchContext
from aminer.parsing.MatchElement import MatchElement
from aminer.parsing.DecimalFloatValueModelElement import DecimalFloatValueModelElement
from unit.TestBase import TestBase, DummyMatchContext, DummyFixedDataModelElement, DummyFirstMatchModelElement


class JsonStringModelElementTest(TestBase):
    """Unittests for the JsonStringModelElement."""

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
        json_me = JsonStringModelElement(self.id_, self.key_parser_dict)
        self.assertEqual(json_me.get_id(), self.id_)

    def test2get_child_elements(self):
        """Test if get_child_elements returns None."""
        k = self.key_parser_dict
        json_me = JsonStringModelElement(self.id_, self.key_parser_dict)
        from pprint import pprint
        print("OUTSCH")
        pprint(json_me.get_child_elements()[0])
        pprint(json_me.get_child_elements()[1])
        self.assertEqual(json_me.get_child_elements(), [
            k["menu"]["id"], k["menu"]["value"], [
                k["menu"]["popup"]["menuitem"][0]["value"], k["menu"]["popup"]["menuitem"][0]["onclick"],
                k["menu"]["popup"]["menuitem"][0]["optional_key_clickable"], k["menu"]["popup"]["menuitem"][1]["value"],
                k["menu"]["popup"]["menuitem"][1]["onclick"], k["menu"]["popup"]["menuitem"][1]["clickable"]]])

#    def test3get_match_element_valid_match(self):
#        """Parse matching substring from MatchContext and check if the MatchContext was updated with all characters."""
#        json_model_element = JsonStringModelElement(self.id_, self.key_parser_dict)
#        data = self.single_line_json
#        value = json.loads(data)
#        match_context = DummyMatchContext(data)
#        match_element = json_model_element.get_match_element(self.path, match_context)
#        match_context.match_string = str(json.loads(match_context.match_string)).encode()
#        self.compare_match_results(
#            data, match_element, match_context, self.id_, self.path, str(value).encode(), value, match_element.children)
#
#        data = self.multi_line_json
#        value = json.loads(data)
#        match_context = DummyMatchContext(data)
#        match_element = json_model_element.get_match_element(self.path, match_context)
#        match_context.match_string = str(json.loads(match_context.match_string)).encode()
#        match_context.match_data = data[len(match_context.match_string):]
#        self.compare_match_results(
#            data, match_element, match_context, self.id_, self.path, str(value).encode(), value, match_element.children)
#
#        data = self.everything_new_line_json
#        value = json.loads(data)
#        match_context = DummyMatchContext(data)
#        match_element = json_model_element.get_match_element(self.path, match_context)
#        match_context.match_string = str(json.loads(match_context.match_string)).encode()
#        match_context.match_data = data[len(match_context.match_string):]
#        self.compare_match_results(
#            data, match_element, match_context, self.id_, self.path, str(value).encode(), value, match_element.children)
#
#        # Test if keys differently ordered than in the key_parser_dict are parsed properly.
#        data = self.single_line_different_order_with_optional_key_json
#        value = json.loads(data)
#        match_context = DummyMatchContext(data)
#        match_element = json_model_element.get_match_element(self.path, match_context)
#        match_context.match_string = str(json.loads(match_context.match_string)).encode()
#        match_context.match_data = data[len(match_context.match_string):]
#        self.compare_match_results(
#            data, match_element, match_context, self.id_, self.path, str(value).encode(), value, match_element.children)
#
#        data = self.single_line_empty_array
#        value = json.loads(data)
#        match_context = DummyMatchContext(data)
#        match_element = json_model_element.get_match_element(self.path, match_context)
#        match_context.match_string = str(json.loads(match_context.match_string)).encode()
#        match_context.match_data = data[len(match_context.match_string):]
#        self.compare_match_results(
#            data, match_element, match_context, self.id_, self.path, str(value).encode(), value, match_element.children)
#
#        json_model_element = JsonStringModelElement(self.id_, self.key_parser_dict_allow_all)
#        data = self.single_line_different_order_with_optional_key_json
#        value = json.loads(data)
#        match_context = DummyMatchContext(data)
#        match_element = json_model_element.get_match_element(self.path, match_context)
#        match_context.match_string = str(value).encode()
#        match_context.match_data = data[len(match_context.match_string):]
#        self.compare_match_results(
#            data, match_element, match_context, self.id_, self.path, str(value).encode(), value, match_element.children)
#
#        json_model_element = JsonStringModelElement(self.id_, self.key_parser_dict_array)
#        data = self.single_line_json_array
#        value = json.loads(data)
#        match_context = DummyMatchContext(data)
#        match_element = json_model_element.get_match_element(self.path, match_context)
#        match_context.match_string = str(value).encode()
#        match_context.match_data = data[len(match_context.match_string):]
#        self.compare_match_results(
#            data, match_element, match_context, self.id_, self.path, str(value).encode(), value, match_element.children)
#
#        json_model_element = JsonStringModelElement(self.id_, self.key_parser_dict_escaped)
#        data = self.single_line_escaped_json.decode("unicode-escape").encode()
#        value = json.loads(data)
#        match_context = DummyMatchContext(data)
#        match_element = json_model_element.get_match_element(self.path, match_context)
#        match_context.match_string = str(value).encode()
#        match_context.match_data = data[len(match_context.match_string):]
#        self.compare_match_results(
#            data, match_element, match_context, self.id_, self.path, str(value).encode(), value, match_element.children)
#
#        json_model_element = JsonStringModelElement(self.id_, self.key_parser_dict_array_of_arrays)
#        data = self.array_of_arrays
#        value = json.loads(data)
#        match_context = DummyMatchContext(data)
#        match_element = json_model_element.get_match_element(self.path, match_context)
#        match_context.match_string = str(json.loads(match_context.match_string)).encode()
#        self.compare_match_results(
#            data, match_element, match_context, self.id_, self.path, str(value).encode(), value, match_element.children)
#

