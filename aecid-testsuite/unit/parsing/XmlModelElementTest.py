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
    """Unittests for the XmlModelElement."""

    id_ = "xml"
    path = "path"
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
</messages>
"""
    key_parser_dict = {"messages": [{"note": {
        "+id": DummyNumberModelElement("id"),
        "_+opt": DummyFixedDataModelElement("opt", b"text"),
        "to": AnyByteDataModelElement("to"),
        "from": AnyByteDataModelElement("from"),
        "?heading": AnyByteDataModelElement("heading"),
        "body": {
            "text1": AnyByteDataModelElement("text1"),
            "text2": AnyByteDataModelElement("text2")
        }
    }}]}
    key_parser_dict_allow_all = {"messages": [{"note": {
        "+id": DummyNumberModelElement("id"),
        "_+opt": DummyFixedDataModelElement("opt", b"text"),
        "to": AnyByteDataModelElement("to"),
        "from": AnyByteDataModelElement("from"),
        "?heading": AnyByteDataModelElement("heading"),
        "body": "ALLOW_ALL"
    }}]}

    def test1get_match_element_valid_match(self):
        """Parse matching substring from MatchContext and check if the MatchContext was updated with all characters."""
        xml_model_element = XmlModelElement(self.id_, self.key_parser_dict)
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

        xml_model_element = XmlModelElement(self.id_, self.key_parser_dict_allow_all)
        data = self.single_line
        value = decode_xml(xml.fromstring(data))
        match_context = DummyMatchContext(data)
        match_element = xml_model_element.get_match_element(self.path, match_context)
        match_context.match_string = data
        self.compare_match_results(
            data, match_element, match_context, self.id_, self.path, data, value, match_element.children)

    def test2get_match_element_with_umlaut(self):
        """Test if ä ö ü are used correctly."""
        key_parser_dict = {"messages": [{"note": {"works": DummyFixedDataModelElement("abc", "a ä ü ö z".encode("utf-8"))}}]}
        data = "<messages><note><works>a ä ü ö z</works></note></messages>".encode("utf-8")
        xml_model_element = XmlModelElement(self.id_, key_parser_dict)
        value = decode_xml(xml.fromstring(data))
        match_context = DummyMatchContext(data)
        match_element = xml_model_element.get_match_element(self.path, match_context)
        match_context.match_string = data
        match_context.match_data = data[len(match_context.match_string):]
        self.compare_match_results(
            data, match_element, match_context, self.id_, self.path, data, value, match_element.children)

    def test3get_match_element_no_match(self):
        """Parse not matching substring from MatchContext and check if the MatchContext was not changed."""
        xml_model_element = XmlModelElement(self.id_, self.key_parser_dict)
        # missing element
        data = self.single_line_missing_element
        match_context = DummyMatchContext(data)
        match_element = xml_model_element.get_match_element(self.path, match_context)
        self.compare_no_match_results(data, match_element, match_context)

        # invalid xml
        data = self.single_line_invalid
        match_context = DummyMatchContext(data)
        match_element = xml_model_element.get_match_element(self.path, match_context)
        self.compare_no_match_results(data, match_element, match_context)

        # child not matching
        data = self.single_line_no_match
        match_context = DummyMatchContext(data)
        match_element = xml_model_element.get_match_element(self.path, match_context)
        self.compare_no_match_results(data, match_element, match_context)

        # non-optional empty
        data = self.single_line_non_optional_empty
        match_context = DummyMatchContext(data)
        match_element = xml_model_element.get_match_element(self.path, match_context)
        self.compare_no_match_results(data, match_element, match_context)

        # no xml
        data = self.single_line_no_xml
        match_context = DummyMatchContext(data)
        match_element = xml_model_element.get_match_element(self.path, match_context)
        self.compare_no_match_results(data, match_element, match_context)

    def test4element_id_input_validation(self):
        """Check if element_id is validated."""
        self.assertRaises(ValueError, XmlModelElement, "", self.key_parser_dict)  # empty element_id
        self.assertRaises(TypeError, XmlModelElement, None, self.key_parser_dict)  # None element_id
        self.assertRaises(TypeError, XmlModelElement, b"path", self.key_parser_dict)  # bytes element_id is not allowed
        self.assertRaises(TypeError, XmlModelElement, True, self.key_parser_dict)  # boolean element_id is not allowed
        self.assertRaises(TypeError, XmlModelElement, 123, self.key_parser_dict)  # integer element_id is not allowed
        self.assertRaises(TypeError, XmlModelElement, 123.22, self.key_parser_dict)  # float element_id is not allowed
        self.assertRaises(TypeError, XmlModelElement, {"id": "path"}, self.key_parser_dict)  # dict element_id is not allowed
        self.assertRaises(TypeError, XmlModelElement, ["path"], self.key_parser_dict)  # list element_id is not allowed
        self.assertRaises(TypeError, XmlModelElement, [], self.key_parser_dict)  # empty list element_id is not allowed
        self.assertRaises(TypeError, XmlModelElement, (), self.key_parser_dict)  # empty tuple element_id is not allowed
        self.assertRaises(TypeError, XmlModelElement, set(), self.key_parser_dict)  # empty set element_id is not allowed

    def test5key_parser_dict_input_validation(self):
        """Check if key_parser_dict is validated."""
        self.assertRaises(TypeError, XmlModelElement, self.id_, "path")  # string key_parser_dict
        self.assertRaises(TypeError, XmlModelElement, self.id_, None)  # None key_parser_dict
        self.assertRaises(TypeError, XmlModelElement, self.id_, b"path")  # bytes key_parser_dict is not allowed
        self.assertRaises(TypeError, XmlModelElement, self.id_, True)  # boolean key_parser_dict is not allowed
        self.assertRaises(TypeError, XmlModelElement, self.id_, 123)  # integer key_parser_dict is not allowed
        self.assertRaises(TypeError, XmlModelElement, self.id_, 123.22)  # float key_parser_dict is not allowed
        # dict key_parser_dict with no ModelElementInterface values is not allowed
        self.assertRaises(TypeError, XmlModelElement, self.id_, {"id": "path"})
        # dict key_parser_dict with list of other lengths than 1 is not allowed.
        key_parser_dict = copy.deepcopy(self.key_parser_dict)
        key_parser_dict["messages"] = []
        self.assertRaises(ValueError, XmlModelElement, self.id_, key_parser_dict)
        self.assertRaises(TypeError, XmlModelElement, self.id_, ["path"])  # list key_parser_dict is not allowed
        self.assertRaises(TypeError, XmlModelElement, self.id_, [])  # empty list key_parser_dict is not allowed
        self.assertRaises(TypeError, XmlModelElement, self.id_, ())  # empty tuple key_parser_dict is not allowed
        self.assertRaises(TypeError, XmlModelElement, self.id_, set())  # empty set key_parser_dict is not allowed

    def test6attribute_prefix_input_validation(self):
        """Check if attribute_prefix is validated."""
        self.assertRaises(ValueError, XmlModelElement, self.id_, self.key_parser_dict, attribute_prefix="")
        self.assertRaises(TypeError, XmlModelElement, self.id_, self.key_parser_dict, attribute_prefix=None)
        self.assertRaises(TypeError, XmlModelElement, self.id_, self.key_parser_dict, attribute_prefix=b"path")
        self.assertRaises(TypeError, XmlModelElement, self.id_, self.key_parser_dict, attribute_prefix=True)
        self.assertRaises(TypeError, XmlModelElement, self.id_, self.key_parser_dict, attribute_prefix=123)
        self.assertRaises(TypeError, XmlModelElement, self.id_, self.key_parser_dict, attribute_prefix=123.22)
        self.assertRaises(TypeError, XmlModelElement, self.id_, self.key_parser_dict, attribute_prefix={"id": "path"})
        self.assertRaises(TypeError, XmlModelElement, self.id_, self.key_parser_dict, attribute_prefix=["path"])
        self.assertRaises(TypeError, XmlModelElement, self.id_, self.key_parser_dict, attribute_prefix=[])
        self.assertRaises(TypeError, XmlModelElement, self.id_, self.key_parser_dict, attribute_prefix=())
        self.assertRaises(TypeError, XmlModelElement, self.id_, self.key_parser_dict, attribute_prefix=set())

    def test7optional_attribute_prefix_input_validation(self):
        """Check if optional_attribute_prefix is validated."""
        self.assertRaises(ValueError, XmlModelElement, self.id_, self.key_parser_dict, optional_attribute_prefix="")
        self.assertRaises(TypeError, XmlModelElement, self.id_, self.key_parser_dict, optional_attribute_prefix=None)
        self.assertRaises(TypeError, XmlModelElement, self.id_, self.key_parser_dict, optional_attribute_prefix=b"path")
        self.assertRaises(TypeError, XmlModelElement, self.id_, self.key_parser_dict, optional_attribute_prefix=True)
        self.assertRaises(TypeError, XmlModelElement, self.id_, self.key_parser_dict, optional_attribute_prefix=123)
        self.assertRaises(TypeError, XmlModelElement, self.id_, self.key_parser_dict, optional_attribute_prefix=123.22)
        self.assertRaises(TypeError, XmlModelElement, self.id_, self.key_parser_dict, optional_attribute_prefix={"id": "path"})
        self.assertRaises(TypeError, XmlModelElement, self.id_, self.key_parser_dict, optional_attribute_prefix=["path"])
        self.assertRaises(TypeError, XmlModelElement, self.id_, self.key_parser_dict, optional_attribute_prefix=[])
        self.assertRaises(TypeError, XmlModelElement, self.id_, self.key_parser_dict, optional_attribute_prefix=())
        self.assertRaises(TypeError, XmlModelElement, self.id_, self.key_parser_dict, optional_attribute_prefix=set())

    def test8empty_allowed_prefix_input_validation(self):
        """Check if empty_allowed_prefix is validated."""
        self.assertRaises(ValueError, XmlModelElement, self.id_, self.key_parser_dict, empty_allowed_prefix="")
        self.assertRaises(TypeError, XmlModelElement, self.id_, self.key_parser_dict, empty_allowed_prefix=None)
        self.assertRaises(TypeError, XmlModelElement, self.id_, self.key_parser_dict, empty_allowed_prefix=b"path")
        self.assertRaises(TypeError, XmlModelElement, self.id_, self.key_parser_dict, empty_allowed_prefix=True)
        self.assertRaises(TypeError, XmlModelElement, self.id_, self.key_parser_dict, empty_allowed_prefix=123)
        self.assertRaises(TypeError, XmlModelElement, self.id_, self.key_parser_dict, empty_allowed_prefix=123.22)
        self.assertRaises(TypeError, XmlModelElement, self.id_, self.key_parser_dict, empty_allowed_prefix={"id": "path"})
        self.assertRaises(TypeError, XmlModelElement, self.id_, self.key_parser_dict, empty_allowed_prefix=["path"])
        self.assertRaises(TypeError, XmlModelElement, self.id_, self.key_parser_dict, empty_allowed_prefix=[])
        self.assertRaises(TypeError, XmlModelElement, self.id_, self.key_parser_dict, empty_allowed_prefix=())
        self.assertRaises(TypeError, XmlModelElement, self.id_, self.key_parser_dict, empty_allowed_prefix=set())

    def test9xml_header_expected_input_validation(self):
        """Check if xml_header_expected is validated."""
        self.assertRaises(TypeError, XmlModelElement, self.id_, self.key_parser_dict, xml_header_expected="")
        self.assertRaises(TypeError, XmlModelElement, self.id_, self.key_parser_dict, xml_header_expected=None)
        self.assertRaises(TypeError, XmlModelElement, self.id_, self.key_parser_dict, xml_header_expected=b"path")
        self.assertRaises(TypeError, XmlModelElement, self.id_, self.key_parser_dict, xml_header_expected=123)
        self.assertRaises(TypeError, XmlModelElement, self.id_, self.key_parser_dict, xml_header_expected=123.22)
        self.assertRaises(TypeError, XmlModelElement, self.id_, self.key_parser_dict, xml_header_expected={"id": "path"})
        self.assertRaises(TypeError, XmlModelElement, self.id_, self.key_parser_dict, xml_header_expected=["path"])
        self.assertRaises(TypeError, XmlModelElement, self.id_, self.key_parser_dict, xml_header_expected=[])
        self.assertRaises(TypeError, XmlModelElement, self.id_, self.key_parser_dict, xml_header_expected=())
        self.assertRaises(TypeError, XmlModelElement, self.id_, self.key_parser_dict, xml_header_expected=set())

    def test10compare_prefixes(self):
        """Check if all prefixes are validated against each other."""
        self.assertRaises(ValueError, XmlModelElement, self.id_, self.key_parser_dict, attribute_prefix="$", optional_attribute_prefix="$")
        self.assertRaises(ValueError, XmlModelElement, self.id_, self.key_parser_dict, attribute_prefix="$", empty_allowed_prefix="$")
        self.assertRaises(ValueError, XmlModelElement, self.id_, self.key_parser_dict, empty_allowed_prefix="$", optional_attribute_prefix="$")


if __name__ == "__main__":
    unittest.main()
