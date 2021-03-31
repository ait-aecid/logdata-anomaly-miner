import unittest
import json
from aminer.parsing.MatchContext import MatchContext
from aminer.parsing.FixedWordlistDataModelElement import FixedWordlistDataModelElement
from aminer.parsing.JsonModelElement import JsonModelElement
from aminer.parsing.VariableByteDataModelElement import VariableByteDataModelElement


class JsonModelElementTest(unittest.TestCase):
    """Unittests for the JsonModelElement."""

    single_line_json = b'{"menu": {"id": "file", "value": "File", "popup": {"menuitem": [{"value": "New", "onclick": "CreateNewDoc()"}, {' \
                       b'"value": "Open", "onclick": "OpenDoc()"}, {"value": "Close", "onclick": "CloseDoc()"}]}}}'
    single_line_with_optional_key_json = b'{"menu": {"id": "file", "value": "File", "popup": {"menuitem": [{"value": "New", "onclick":' \
                                         b' "CreateNewDoc()", "clickable": false}, {"value": "Open", "onclick": "OpenDoc()"}, {"value": ' \
                                         b'"Close", "onclick": "CloseDoc()", "clickable": false}]}}}'
    single_line_missing_key_json = b'{"menu": {"id": "file", "popup": {"menuitem": [{"value": "New", "onclick": "CreateNewDoc()"}, {' \
                                   b'"value": "Open", "onclick": "OpenDoc()"}, {"value": "Close", "onclick": "CloseDoc()"}]}}}'
    single_line_different_order_with_optional_key_json = \
        b'{"menu": {"value": "File","popup": {"menuitem": [{"clickable": false, "value": "New", "onclick": "CreateNewDoc()"}, {' \
        b'"onclick": "OpenDoc()", "value": "Open"}, {"value": "Close", "onclick": "CloseDoc()", "clickable": false}]}, "id": "file"}}'
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
    alphabet = b'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ 0123456789_-.'
    key_parser_dict = {'menu': {
        'id': VariableByteDataModelElement('id', alphabet),
        'value': VariableByteDataModelElement('value', alphabet),
        'popup': {
            'menuitem': [{
                'value': FixedWordlistDataModelElement('buttonNames', [b'New', b'Open', b'Close']),
                'onclick': FixedWordlistDataModelElement('buttonOnclick', [b'CreateNewDoc()', b'OpenDoc()', b'CloseDoc()']),
                'optional_key_clickable': FixedWordlistDataModelElement('clickable', [b'true', b'false'])
            }]
        }}}
    key_parser_dict_allow_all = {'menu': {
        'id': VariableByteDataModelElement('id', alphabet),
        'value': VariableByteDataModelElement('value', alphabet),
        'popup': 'ALLOW_ALL'
    }}

    def test1get_valid_match_elements(self):
        """Get valid json elements with different formats."""
        json_model_element = JsonModelElement('json', self.key_parser_dict)
        match = json_model_element.get_match_element('match', MatchContext(self.single_line_json))
        self.assertEqual(match.match_object, json.loads(self.single_line_json))

        match = json_model_element.get_match_element('match', MatchContext(self.multi_line_json))
        self.assertEqual(match.match_object, json.loads(self.multi_line_json))

        match = json_model_element.get_match_element('match', MatchContext(self.everything_new_line_json))
        self.assertEqual(match.match_object, json.loads(self.everything_new_line_json))

    def test2optional_key_prefix(self):
        """Validate optional keys with the optional_key_prefix."""
        json_model_element = JsonModelElement('json', self.key_parser_dict)
        match = json_model_element.get_match_element('match', MatchContext(self.single_line_with_optional_key_json))
        self.assertEqual(match.match_object, json.loads(self.single_line_with_optional_key_json))

    def test3missing_key(self):
        """Check if no match is returned if a key is missing."""
        json_model_element = JsonModelElement('json', self.key_parser_dict)
        match = json_model_element.get_match_element('match', MatchContext(self.single_line_missing_key_json))
        self.assertEqual(match, None)

    def test4allow_all_dict(self):
        """Test a simplified key_parser_dict with ALLOW_ALL."""
        json_model_element = JsonModelElement('json', self.key_parser_dict_allow_all)
        match = json_model_element.get_match_element('match', MatchContext(self.single_line_json))
        self.assertEqual(match.match_object, json.loads(self.single_line_json))

        match = json_model_element.get_match_element('match', MatchContext(self.multi_line_json))
        self.assertEqual(match.match_object, json.loads(self.multi_line_json))

        match = json_model_element.get_match_element('match', MatchContext(self.everything_new_line_json))
        self.assertEqual(match.match_object, json.loads(self.everything_new_line_json))

    def test5different_order_keys(self):
        """Test if keys differently ordered than in the key_parser_dict are parsed properly."""
        json_model_element = JsonModelElement('json', self.key_parser_dict)
        match = json_model_element.get_match_element('match', MatchContext(self.single_line_different_order_with_optional_key_json))
        self.assertEqual(match.match_object, json.loads(self.single_line_different_order_with_optional_key_json))

        json_model_element = JsonModelElement('json', self.key_parser_dict_allow_all)
        match = json_model_element.get_match_element('match', MatchContext(self.single_line_different_order_with_optional_key_json))
        self.assertEqual(match.match_object, json.loads(self.single_line_different_order_with_optional_key_json))

    def test6null_value(self):
        """Test if null values are parsed to "null"."""
        key_parser_dict = {
            "works": VariableByteDataModelElement("id", b"abc123"),
            "problem": FixedWordlistDataModelElement("wordlist", [b"allowed value", b"null"])}
        data1 = b"""{
            "works": "abc",
            "problem": "allowed value"
        }"""
        data2 = b"""{
            "works": "123",
            "problem": null
        }"""
        json_model_element = JsonModelElement('json', key_parser_dict)
        self.assertIsNotNone(json_model_element.get_match_element('match', MatchContext(data1)))
        self.assertIsNotNone(json_model_element.get_match_element('match', MatchContext(data2)))


if __name__ == "__main__":
    unittest.main()
