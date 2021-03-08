import unittest
from aminer.parsing.Base64StringModelElement import Base64StringModelElement
from unit.TestBase import TestBase, DummyMatchContext
import base64


class Base64StringModelElementTest(TestBase):
    """Unittests for the Base64StringModelElement."""

    base64_string_model_element = Base64StringModelElement('base64')
    match_base64 = 'match/base64'

    def test1get_id(self):
        """Test if get_id works properly."""
        base64_dme = Base64StringModelElement("s0")
        self.assertEqual(base64_dme.get_id(), "s0")

    def test2get_child_elements(self):
        """Test if get_child_elements returns None."""
        base64_dme = Base64StringModelElement("s0")
        self.assertEqual(base64_dme.get_child_elements(), None)

    def test3get_match_element_valid_match_string_with_padding(self):
        """Parse matching substring with padding from MatchContext and check if the MatchContext was updated accordingly."""
        string = b'This is some string to be encoded.'
        base64_string = b'VGhpcyBpcyBzb21lIHN0cmluZyB0byBiZSBlbmNvZGVkLg=='
        dummy_match_context = DummyMatchContext(base64_string)
        base64_dme = Base64StringModelElement("s0")
        match_element = base64_dme.get_match_element("base64", dummy_match_context)
        self.assertEqual(match_element.path, "base64/s0")
        self.assertEqual(match_element.match_string, base64_string)
        self.assertEqual(match_element.match_object, string)
        self.assertIsNone(match_element.children, None)
        self.assertEqual(dummy_match_context.match_data, base64_string)

    def test4get_match_element_valid_match_string_without_padding(self):
        """Parse matching substring with padding from MatchContext and check if the MatchContext was updated accordingly."""
        string = b'This is some string to be encoded without the padding character =.'
        base64_string = b'VGhpcyBpcyBzb21lIHN0cmluZyB0byBiZSBlbmNvZGVkIHdpdGhvdXQgdGhlIHBhZGRpbmcgY2hhcmFjdGVyID0u'
        dummy_match_context = DummyMatchContext(base64_string)
        base64_dme = Base64StringModelElement("s0")
        match_element = base64_dme.get_match_element("base64", dummy_match_context)
        self.assertEqual(match_element.path, "base64/s0")
        self.assertEqual(match_element.match_string, base64_string)
        self.assertEqual(match_element.match_object, string)
        self.assertIsNone(match_element.children, None)
        self.assertEqual(dummy_match_context.match_data, base64_string)

    def test4get_match_element_no_match(self):
        """Parse not matching substring from MatchContext and check if the MatchContext was not changed."""
        data = b"Hello World."
        dummy_match_context = DummyMatchContext(data)
        base64_dme = Base64StringModelElement("s0")
        match_element = base64_dme.get_match_element("fixed", dummy_match_context)
        self.assertIsNone(match_element, None)
        self.assertEqual(dummy_match_context.match_data, data)

    def test5element_id_input_validation(self):
        """Check if element_id is validated."""
        fixed_string = b"string"
        # empty element_id
        element_id = ""
        self.assertRaises(ValueError, Base64StringModelElement, element_id)

        # bytes element_id is not allowed
        element_id = b"path"
        self.assertRaises(ValueError, Base64StringModelElement, element_id)

        # integer element_id is not allowed
        element_id = 123
        self.assertRaises(ValueError, Base64StringModelElement, element_id)

        # float element_id is not allowed
        element_id = 123.22
        self.assertRaises(ValueError, Base64StringModelElement, element_id)

        # dict element_id is not allowed
        element_id = {"id": "path"}
        self.assertRaises(ValueError, Base64StringModelElement, element_id)

        # list element_id is not allowed
        element_id = ["path"]
        self.assertRaises(ValueError, Base64StringModelElement, element_id)

    def test2_base64_string_with_wrong_characters(self):
        """
        In this test case some base64 strings with not allowed characters are matched with the ModelElement.
        Also the padding checks of base64 strings is tested.
        """
        # string with padding
        string = b'This is some string to be encoded.'
        string_after_padding = b'This+string+is+not+encoded+any+more+'
        base64_string = base64.b64encode(string)
        match_context = MatchContext(base64_string + string_after_padding + b'!')
        match_element = self.base64_string_model_element.get_match_element('match', match_context)
        self.assertEqual(match_element.get_path(), self.match_base64)
        self.assertEqual(match_element.get_match_string(), base64_string)
        self.assertEqual(match_element.get_match_object(), string)
        self.assertEqual(match_element.get_children(), None)
        self.assertEqual(match_context.match_data, string_after_padding + b'!')

        # string without padding
        string = b'This is some string to be encoded without the padding character =.'
        base64_string = base64.b64encode(string)
        match_context = MatchContext(base64_string + string_after_padding + b'!')
        match_element = self.base64_string_model_element.get_match_element('match', match_context)
        self.assertEqual(match_element.get_path(), self.match_base64)
        self.assertEqual(match_element.get_match_string(), base64_string + string_after_padding)
        self.assertEqual(match_element.get_match_object(), string + base64.b64decode(string_after_padding))
        self.assertEqual(match_element.get_children(), None)
        self.assertEqual(match_context.match_data, b'!')


if __name__ == "__main__":
    unittest.main()
