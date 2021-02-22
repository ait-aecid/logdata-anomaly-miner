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
          "onclick": "OpenDoc()"},
        {
          "value": "Close",
          "onclick": "CloseDoc()"}
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


if __name__ == "__main__":
    unittest.main()
