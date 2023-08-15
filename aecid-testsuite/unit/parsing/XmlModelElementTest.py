import copy
import unittest
import xml.etree.ElementTree as xml
import json
from aminer.parsing.XmlModelElement import XmlModelElement, decode_xml
from aminer.parsing.MatchContext import MatchContext
from aminer.parsing.MatchElement import MatchElement
from aminer.parsing.AnyByteDataModelElement import AnyByteDataModelElement
from unit.TestBase import TestBase, DummyMatchContext, DummyFixedDataModelElement, DummyFirstMatchModelElement, DummyNumberModelElement


class XmlModelElementTest(TestBase):
    """Unittests for the JsonModelElement."""

    id_ = "xml"
    path = "path"
    root = "messages"
    single_line = b"<messages><note id=\"501\"><to>Tove</to><from>Jani</from><heading/><body><text1>Don't forget me this weekend!</text1><text2>Don't forget me this weekend!</text2></body>" \
                  b"</note><note id=\"502\" opt=\"text\"><to>Jani</to><from>Tove</from><heading>Re: </heading><body><text1>I will not</text1><text2>I will not</text2></body></note></messages>"
    single_line_missing_element = b"<messages><note id=\"501\"><from>Jani</from><heading></heading><body><text1>Don't forget me this weekend!</text1><text2>Don't forget me this weekend!</text2></body></messages>"
    single_line_invalid = b"<note id=\"501\"><to>Tove</to><from>Jani</from><heading></heading><body><text1>Don't forget me this weekend!</text1><text2>Don't forget me this weekend!</text2></body>" \
                  b"</note><note id=\"502\" opt=\"text\"><to>Jani</to><from>Tove</from><heading>Re: </heading><body><text1>I will not</text1><text2>I will not</text2></body></note>"
    single_line_no_match = b"<notes><note id=\"501\"><to>Tove</to><from>Jani</from><heading></heading><body><text1>Don't forget me this weekend!</text1><text2>Don't forget me this weekend!</text2></body>" \
                  b"</note><note id=\"502\" opt=\"text\"><to>Jani</to><from>Tove</from><heading>Re: </heading><body><text1>I will not</text1><text2>I will not</text2></body></note></notes>"
    single_line_non_optional_empty = b"<messages><note id=\"501\"><to>Tove</to><from></from><heading/><body><text1>Don't forget me this weekend!</text1><text2>Don't forget me this weekend!</text2></body>" \
                  b"</note><note id=\"502\" opt=\"text\"><to>Jani</to><from>Tove</from><heading>Re: </heading><body><text1>I will not</text1><text2>I will not</text2></body></note></messages>"
    single_line_no_xml = b"<messages><note id=\"501\"><to>Tove</to><from>Jani</from><heading/><body><text1>Don't forget me this weekend!</text1><text2>Don't forget me this weekend!</text2></body>" \
                         b"</note><note id=\"502\" opt=\"text\"><to>Jani</to><from>Tove</from><heading>Re: </heading><body><text1>I will not</text1><text2>I will not</text2></body></note></messages>ddddddddddddddd"
    single_line_escaped = b"<messages><note id=\"501\"><to>Tove</to><from>Jani</from><heading/><body><text1>Don't forget me this weekend!</text1><text2>Don't forget me this weekend!</text2></body>" \
                  b"</note><note id=\"502\" opt=\"text\"><to>Jani</to><from>Tove</from><heading>Re: </heading><body><text1>I\x20will\x20not</text1><text2>I\x20will\x20not</text2></body></note></messages>"
    single_line_xml_declaration = b"<?xml version=\"1.0\" encoding=\"UTF-8\"?>" \
                  b"<messages><note id=\"501\"><to>Tove</to><from>Jani</from><heading/><body><text1>Don't forget me this weekend!</text1><text2>Don't forget me this weekend!</text2></body>" \
                  b"</note><note id=\"502\" opt=\"text\"><to>Jani</to><from>Tove</from><heading>Re: </heading><body><text1>I will not</text1><text2>I will not</text2></body></note></messages>"
    multi_line = b"""<messages>
  <note id="501">
    <to>Tove</to>
    <from>Jani</from>
    <heading></heading>
    <body>
      <text1>Don't forget me this weekend!</text1>
      <text2>Don't forget me this weekend!</text2>
    </body>
  </note>
  <note id="502" opt="text">
    <to>Jani</to>
    <from>Tove</from>
    <heading>Re: </heading>
    <body>
      <text1>test1</text1>
      <text2>test2</text2>
    </body>
  </note>
</messages>"""
    key_parser_dict = {"messages": [{"note": {
        "!id": DummyNumberModelElement("id"),
        "_!opt": AnyByteDataModelElement("opt"),
        "to": AnyByteDataModelElement("to"),
        "from": AnyByteDataModelElement("from"),
        "?heading": AnyByteDataModelElement("heading"),
        "body": {
            "text1": AnyByteDataModelElement("text1"),
            "text2": AnyByteDataModelElement("text2")
        }
    }}]}
    key_parser_dict_allow_all = {"messages": [{"note": {
        "!id": DummyNumberModelElement("id"),
        "to": AnyByteDataModelElement("to"),
        "from": AnyByteDataModelElement("from"),
        "?heading": AnyByteDataModelElement("heading"),
        "body": "ALLOW_ALL"
    }}]}

    def test1get_match_element_valid_match(self):
        """Parse matching substring from MatchContext and check if the MatchContext was updated with all characters."""
        xml_model_element = XmlModelElement(self.id_, self.root, self.key_parser_dict)
        data = self.single_line
        value = decode_xml(xml.fromstring(data))
        match_context = DummyMatchContext(data)
        match_element = xml_model_element.get_match_element(self.path, match_context)
        match_context.match_string = data
        self.compare_match_results(
            data, match_element, match_context, self.id_, self.path, data, value, match_element.children)

        data = self.multi_line
        value = decode_xml(xml.fromstring(data))
        match_context = DummyMatchContext(data)
        match_element = xml_model_element.get_match_element(self.path, match_context)
        match_context.match_string = data
        self.compare_match_results(
            data, match_element, match_context, self.id_, self.path, data, value, match_element.children)

        data = self.single_line_escaped
        value = decode_xml(xml.fromstring(data))
        match_context = DummyMatchContext(self.single_line_escaped)
        match_element = xml_model_element.get_match_element(self.path, match_context)
        match_context.match_string = self.single_line
        self.compare_match_results(
            data, match_element, match_context, self.id_, self.path, self.single_line, value, match_element.children)

        data = self.single_line_xml_declaration
        value = decode_xml(xml.fromstring(data))
        match_context = DummyMatchContext(data)
        match_element = xml_model_element.get_match_element(self.path, match_context)
        match_context.match_string = self.single_line
        match_context.match_data = data[len(match_context.match_string):]
        self.compare_match_results(
            data, match_element, match_context, self.id_, self.path, self.single_line, value, match_element.children)

    # def test2get_match_element_with_umlaut(self):
    #     """Test if ä ö ü are used correctly."""
    #     key_parser_dict = {"works": DummyFixedDataModelElement("abc", "a ä ü ö z".encode("utf-8"))}
    #     data = """{
    #         "works": "a ä ü ö z"
    #     }""".encode("utf-8")
    #     json_model_element = JsonModelElement(self.id_, key_parser_dict)
    #     value = json.loads(data)
    #     match_context = DummyMatchContext(data)
    #     match_element = json_model_element.get_match_element(self.path, match_context)
    #     match_context.match_string = str(value).encode()
    #     match_context.match_data = data[len(match_context.match_string):]
    #     self.compare_match_results(
    #         data, match_element, match_context, self.id_, self.path, str(value).encode(), value, match_element.children)
    #
    # def test3get_match_element_no_match(self):
    #     """Parse not matching substring from MatchContext and check if the MatchContext was not changed."""
    #     json_model_element = JsonModelElement(self.id_, self.key_parser_dict)
    #     # missing key
    #     data = self.single_line_missing_key_json
    #     match_context = DummyMatchContext(data)
    #     match_element = json_model_element.get_match_element(self.path, match_context)
    #     self.compare_no_match_results(data, match_element, match_context)
    #
    #     # object instead of array
    #     data = self.single_line_object_instead_of_array
    #     match_context = DummyMatchContext(data)
    #     match_element = json_model_element.get_match_element(self.path, match_context)
    #     self.compare_no_match_results(data, match_element, match_context)
    #
    #     # invalid json
    #     data = self.single_line_invalid_json
    #     match_context = DummyMatchContext(data)
    #     match_element = json_model_element.get_match_element(self.path, match_context)
    #     self.compare_no_match_results(data, match_element, match_context)
    #
    #     # child not matching
    #     data = self.single_line_no_match_json
    #     match_context = DummyMatchContext(data)
    #     match_element = json_model_element.get_match_element(self.path, match_context)
    #     self.compare_no_match_results(data, match_element, match_context)
    #
    #     # all keys missing
    #     data = b"{}"
    #     match_context = DummyMatchContext(data)
    #     match_element = json_model_element.get_match_element(self.path, match_context)
    #     self.compare_no_match_results(data, match_element, match_context)
    #
    #     json_model_element = JsonModelElement(self.id_, self.empty_key_parser_dict)
    #     data = b"[]"
    #     match_context = DummyMatchContext(data)
    #     match_element = json_model_element.get_match_element(self.path, match_context)
    #     self.compare_no_match_results(data, match_element, match_context)
    #
    #     data = b"{[]}"
    #     match_context = DummyMatchContext(data)
    #     match_element = json_model_element.get_match_element(self.path, match_context)
    #     self.compare_no_match_results(data, match_element, match_context)
    #
    #     data = b'{"key": []}'
    #     match_context = DummyMatchContext(data)
    #     match_element = json_model_element.get_match_element(self.path, match_context)
    #     self.compare_no_match_results(data, match_element, match_context)
    #
    #     key_parser_dict = {"a": [{"b": DummyFixedDataModelElement("b", b"ef")}]}
    #     json_model_element = JsonModelElement(self.id_, key_parser_dict)
    #     data = b'{"a": [{"b": "fe"}]}'
    #     match_context = DummyMatchContext(data)
    #     match_element = json_model_element.get_match_element(self.path, match_context)
    #     self.compare_no_match_results(data, match_element, match_context)
    #
    #     key_parser_dict = {"a": [DummyFixedDataModelElement("a", b"gh")]}
    #     json_model_element = JsonModelElement(self.id_, key_parser_dict)
    #     data = b'{"a": ["hg"]}'
    #     match_context = DummyMatchContext(data)
    #     match_element = json_model_element.get_match_element(self.path, match_context)
    #     self.compare_no_match_results(data, match_element, match_context)
    #
    #     key_parser_dict = {"a": {"b": DummyFixedDataModelElement("c", b"c")}}
    #     json_model_element = JsonModelElement(self.id_, key_parser_dict)
    #     data = b'{"a": "b"}'
    #     match_context = DummyMatchContext(data)
    #     match_element = json_model_element.get_match_element(self.path, match_context)
    #     self.compare_no_match_results(data, match_element, match_context)
    #
    # def test12element_id_input_validation(self):
    #     """Check if element_id is validated."""
    #     self.assertRaises(ValueError, JsonModelElement, "", self.key_parser_dict)  # empty element_id
    #     self.assertRaises(TypeError, JsonModelElement, None, self.key_parser_dict)  # None element_id
    #     self.assertRaises(TypeError, JsonModelElement, b"path", self.key_parser_dict)  # bytes element_id is not allowed
    #     self.assertRaises(TypeError, JsonModelElement, True, self.key_parser_dict)  # boolean element_id is not allowed
    #     self.assertRaises(TypeError, JsonModelElement, 123, self.key_parser_dict)  # integer element_id is not allowed
    #     self.assertRaises(TypeError, JsonModelElement, 123.22, self.key_parser_dict)  # float element_id is not allowed
    #     self.assertRaises(TypeError, JsonModelElement, {"id": "path"}, self.key_parser_dict)  # dict element_id is not allowed
    #     self.assertRaises(TypeError, JsonModelElement, ["path"], self.key_parser_dict)  # list element_id is not allowed
    #     self.assertRaises(TypeError, JsonModelElement, [], self.key_parser_dict)  # empty list element_id is not allowed
    #     self.assertRaises(TypeError, JsonModelElement, (), self.key_parser_dict)  # empty tuple element_id is not allowed
    #     self.assertRaises(TypeError, JsonModelElement, set(), self.key_parser_dict)  # empty set element_id is not allowed
    #
    # def test13key_parser_dict_input_validation(self):
    #     """Check if key_parser_dict is validated."""
    #     self.assertRaises(TypeError, JsonModelElement, self.id_, "path")  # string key_parser_dict
    #     self.assertRaises(TypeError, JsonModelElement, self.id_, None)  # None key_parser_dict
    #     self.assertRaises(TypeError, JsonModelElement, self.id_, b"path")  # bytes key_parser_dict is not allowed
    #     self.assertRaises(TypeError, JsonModelElement, self.id_, True)  # boolean key_parser_dict is not allowed
    #     self.assertRaises(TypeError, JsonModelElement, self.id_, 123)  # integer key_parser_dict is not allowed
    #     self.assertRaises(TypeError, JsonModelElement, self.id_, 123.22)  # float key_parser_dict is not allowed
    #     # dict key_parser_dict with no ModelElementInterface values is not allowed
    #     self.assertRaises(TypeError, JsonModelElement, self.id_, {"id": "path"})
    #     # dict key_parser_dict with list of other lengths than 1 is not allowed.
    #     key_parser_dict = copy.deepcopy(self.key_parser_dict)
    #     key_parser_dict["menu"]["popup"]["menuitem"] = []
    #     self.assertRaises(ValueError, JsonModelElement, self.id_, key_parser_dict)
    #     self.assertRaises(TypeError, JsonModelElement, self.id_, ["path"])  # list key_parser_dict is not allowed
    #     self.assertRaises(TypeError, JsonModelElement, self.id_, [])  # empty list key_parser_dict is not allowed
    #     self.assertRaises(TypeError, JsonModelElement, self.id_, ())  # empty tuple key_parser_dict is not allowed
    #     self.assertRaises(TypeError, JsonModelElement, self.id_, set())  # empty set key_parser_dict is not allowed
    #
    # def test14optional_key_prefix_input_validation(self):
    #     """Check if optional_key_prefix is validated."""
    #     self.assertRaises(ValueError, JsonModelElement, self.id_, self.key_parser_dict, optional_key_prefix="")
    #     self.assertRaises(TypeError, JsonModelElement, self.id_, self.key_parser_dict, optional_key_prefix=None)
    #     self.assertRaises(TypeError, JsonModelElement, self.id_, self.key_parser_dict, optional_key_prefix=b"path")
    #     self.assertRaises(TypeError, JsonModelElement, self.id_, self.key_parser_dict, optional_key_prefix=True)
    #     self.assertRaises(TypeError, JsonModelElement, self.id_, self.key_parser_dict, optional_key_prefix=123)
    #     self.assertRaises(TypeError, JsonModelElement, self.id_, self.key_parser_dict, optional_key_prefix=123.22)
    #     self.assertRaises(TypeError, JsonModelElement, self.id_, self.key_parser_dict, optional_key_prefix={"id": "path"})
    #     self.assertRaises(TypeError, JsonModelElement, self.id_, self.key_parser_dict, optional_key_prefix=["path"])
    #     self.assertRaises(TypeError, JsonModelElement, self.id_, self.key_parser_dict, optional_key_prefix=[])
    #     self.assertRaises(TypeError, JsonModelElement, self.id_, self.key_parser_dict, optional_key_prefix=())
    #     self.assertRaises(TypeError, JsonModelElement, self.id_, self.key_parser_dict, optional_key_prefix=set())
    #
    # def test15nullable_key_prefix_input_validation(self):
    #     """Check if optional_key_prefix is validated."""
    #     self.assertRaises(ValueError, JsonModelElement, self.id_, self.key_parser_dict, nullable_key_prefix="")
    #     self.assertRaises(TypeError, JsonModelElement, self.id_, self.key_parser_dict, nullable_key_prefix=None)
    #     self.assertRaises(TypeError, JsonModelElement, self.id_, self.key_parser_dict, nullable_key_prefix=b"path")
    #     self.assertRaises(TypeError, JsonModelElement, self.id_, self.key_parser_dict, nullable_key_prefix=True)
    #     self.assertRaises(TypeError, JsonModelElement, self.id_, self.key_parser_dict, nullable_key_prefix=123)
    #     self.assertRaises(TypeError, JsonModelElement, self.id_, self.key_parser_dict, nullable_key_prefix=123.22)
    #     self.assertRaises(TypeError, JsonModelElement, self.id_, self.key_parser_dict, nullable_key_prefix={"id": "path"})
    #     self.assertRaises(TypeError, JsonModelElement, self.id_, self.key_parser_dict, nullable_key_prefix=["path"])
    #     self.assertRaises(TypeError, JsonModelElement, self.id_, self.key_parser_dict, nullable_key_prefix=[])
    #     self.assertRaises(TypeError, JsonModelElement, self.id_, self.key_parser_dict, nullable_key_prefix=())
    #     self.assertRaises(TypeError, JsonModelElement, self.id_, self.key_parser_dict, nullable_key_prefix=set())
    #
    # def test16allow_all_fields_input_validation(self):
    #     """Check if allow_all_fields is validated."""
    #     self.assertRaises(TypeError, JsonModelElement, self.id_, self.key_parser_dict, allow_all_fields="")
    #     self.assertRaises(TypeError, JsonModelElement, self.id_, self.key_parser_dict, allow_all_fields=None)
    #     self.assertRaises(TypeError, JsonModelElement, self.id_, self.key_parser_dict, allow_all_fields=b"path")
    #     self.assertRaises(TypeError, JsonModelElement, self.id_, self.key_parser_dict, allow_all_fields=123)
    #     self.assertRaises(TypeError, JsonModelElement, self.id_, self.key_parser_dict, allow_all_fields=123.22)
    #     self.assertRaises(TypeError, JsonModelElement, self.id_, self.key_parser_dict, allow_all_fields={"id": "path"})
    #     self.assertRaises(TypeError, JsonModelElement, self.id_, self.key_parser_dict, allow_all_fields=["path"])
    #     self.assertRaises(TypeError, JsonModelElement, self.id_, self.key_parser_dict, allow_all_fields=[])
    #     self.assertRaises(TypeError, JsonModelElement, self.id_, self.key_parser_dict, allow_all_fields=())
    #     self.assertRaises(TypeError, JsonModelElement, self.id_, self.key_parser_dict, allow_all_fields=set())
    #
    # def test17get_match_element_match_context_input_validation(self):
    #     """Check if an exception is raised, when other classes than MatchContext are used in get_match_element."""
    #     model_element = JsonModelElement(self.id_, self.key_parser_dict)
    #     data = b"abcdefghijklmnopqrstuvwxyz.!?"
    #     model_element.get_match_element(self.path, DummyMatchContext(data))
    #     model_element.get_match_element(self.path, MatchContext(data))
    #
    #     self.assertRaises(AttributeError, model_element.get_match_element, self.path, MatchElement(None, data, None, None))
    #     self.assertRaises(AttributeError, model_element.get_match_element, self.path, data)
    #     self.assertRaises(AttributeError, model_element.get_match_element, self.path, data.decode())
    #     self.assertRaises(AttributeError, model_element.get_match_element, self.path, 123)
    #     self.assertRaises(AttributeError, model_element.get_match_element, self.path, 123.22)
    #     self.assertRaises(AttributeError, model_element.get_match_element, self.path, True)
    #     self.assertRaises(AttributeError, model_element.get_match_element, self.path, None)
    #     self.assertRaises(AttributeError, model_element.get_match_element, self.path, [])
    #     self.assertRaises(AttributeError, model_element.get_match_element, self.path, {"key": MatchContext(data)})
    #     self.assertRaises(AttributeError, model_element.get_match_element, self.path, set())
    #     self.assertRaises(AttributeError, model_element.get_match_element, self.path, ())
    #     self.assertRaises(AttributeError, model_element.get_match_element, self.path, model_element)
    #
    # def test18same_optional_key_and_nullable_key_prefix(self):
    #     """Test if an exception is thrown if the optional_key_prefix is the same as the nullable_key_prefix."""
    #     self.assertRaises(ValueError, JsonModelElement, self.id_, self.key_parser_dict, optional_key_prefix="+", nullable_key_prefix="+")

if __name__ == "__main__":
    unittest.main()
