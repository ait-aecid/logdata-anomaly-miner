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
    strict = False
    ignore_null = True

    def test1get_id(self):
        """Test if get_id works properly."""
        json_me = JsonStringModelElement(self.id_, {}, self.strict, self.ignore_null)
        self.assertEqual(json_me.get_id(), self.id_)

    def test2get_match_element_valid_match(self):
        """Parses a json-file and compares if the configured ModelElements are parsed properly"""
        host = DummyFixedDataModelElement("host", b"www.google.com")
        user = DummyFixedDataModelElement("user", b"foobar")

        key_parser_dict = { "host": host, "user": user }

        json_model_element = JsonStringModelElement(self.id_, key_parser_dict, self.strict, self.ignore_null)
        data = b'{"host": "www.google.com", "user": "foobar", "one": "two"}'
        match_context = DummyMatchContext(data)
        match_element = json_model_element.get_match_element(self.path, match_context)
        self.assertEqual(2, len(match_element.children))
        self.assertEqual(b"www.google.com", match_element.children[0].get_match_object())
        self.assertEqual(b"foobar", match_element.children[1].get_match_object())

    def test3strict_mode(self):
        """Parses a json-file and compares if the configured ModelElements are parsed properly with strict_mode"""
        host = DummyFixedDataModelElement("host", b"www.google.com")
        user = DummyFixedDataModelElement("user", b"foobar")
        path = DummyFixedDataModelElement("path", b"/index.html")

        key_parser_dict = { "host": { "server": host }, "user": user }

        # Sets strict_mode to True
        json_model_element = JsonStringModelElement(self.id_, key_parser_dict, True, self.ignore_null)
        # "one": "two" is too much
        data = b'{"host": {"server": "www.google.com"}, "user": "foobar", "one": "two"}'
        match_context = DummyMatchContext(data)
        match_element = json_model_element.get_match_element(self.path, match_context)
        self.assertEqual(None,match_element)

        # Sets one more element
        key_parser_dict = { "host": { "server": host }, "user": user, "path": path }

        # Sets strict_mode to True
        json_model_element = JsonStringModelElement(self.id_, key_parser_dict, True)
        # "one": "two" is too much
        data = b'{"host": {"server": "www.google.com"}, "user": "foobar", "one": "two"}'
        match_context = DummyMatchContext(data)
        match_element = json_model_element.get_match_element(self.path, match_context)
        self.assertEqual(None,match_element)

        # Sets the logdata to the exact configuration-json.
        data = b'{"host": {"server": "www.google.com"}, "user": "foobar", "path": "/index.html"}'
        match_context = DummyMatchContext(data)
        match_element = json_model_element.get_match_element(self.path, match_context)
        self.assertEqual(3,len(match_element.children))
        self.assertEqual(b"www.google.com", match_element.children[0].get_match_object())
        self.assertEqual(b"foobar", match_element.children[1].get_match_object())
        self.assertEqual(b"/index.html", match_element.children[2].get_match_object())

    def test4ignore_null(self):
        """Parses a json-file with ignore_null and compares if the configured ModelElements are parsed properly"""
        host = DummyFixedDataModelElement("host", b"www.google.com")
        user = DummyFixedDataModelElement("user", b"foobar")

        key_parser_dict = { "host": host, "user": user }

        # Set ignore_null to True and strict to False
        json_model_element = JsonStringModelElement(self.id_, key_parser_dict, False, True)
        # Set user to null
        data = b'{"host": "www.google.com", "user": null, "one": "two"}'
        match_context = DummyMatchContext(data)
        match_element = json_model_element.get_match_element(self.path, match_context)
        # Line must be parsed but without "user":
        self.assertEqual(1, len(match_element.children))
        self.assertEqual(b"www.google.com", match_element.children[0].get_match_object())
        
        # set ignore_null to False and strict to False
        json_model_element = JsonStringModelElement(self.id_, key_parser_dict, False, False)
        # Set user to null
        data = b'{"host": "www.google.com", "user": null, "one": "two"}'
        match_context = DummyMatchContext(data)
        match_element = json_model_element.get_match_element(self.path, match_context)
        # expect an unparsed line
        self.assertEqual(None,match_element)

        # set example user to empty string
        user = DummyFixedDataModelElement("user", b"")
        key_parser_dict2 = { "host": host, "user": user }

        # Set ignore_null to False in order to pass b"" to the subparser. Strict is False
        json_model_element = JsonStringModelElement(self.id_, key_parser_dict2, False, False)
        # Set user to null
        data = b'{"host": "www.google.com", "user": null}'
        match_context = DummyMatchContext(data)
        match_element = json_model_element.get_match_element(self.path, match_context)
        # Line must be parsed:
        self.assertEqual(2, len(match_element.children))
        self.assertEqual(b"www.google.com", match_element.children[0].get_match_object())
        self.assertEqual(b"", match_element.children[1].get_match_object())

        # Set ignore_null to True and strict to True
        json_model_element = JsonStringModelElement(self.id_, key_parser_dict, True, True)
        # Set user to null
        data = b'{"host": "www.google.com", "user": null}'
        match_context = DummyMatchContext(data)
        match_element = json_model_element.get_match_element(self.path, match_context)
        # Line must be parsed but without "user":
        self.assertEqual(1, len(match_element.children))
        self.assertEqual(b"www.google.com", match_element.children[0].get_match_object())
        
        # set ignore_null to False and strict to True
        json_model_element = JsonStringModelElement(self.id_, key_parser_dict, True, False)
        # Set user to null
        data = b'{"host": "www.google.com", "user": null}'
        match_context = DummyMatchContext(data)
        match_element = json_model_element.get_match_element(self.path, match_context)
        # expect an unparsed line
        self.assertEqual(None,match_element)

        # set example user to empty string
        user = DummyFixedDataModelElement("user", b"")
        key_parser_dict2 = { "host": host, "user": user }

        # Set ignore_null to False in order to pass b"" to the subparser. Strict is True
        json_model_element = JsonStringModelElement(self.id_, key_parser_dict2, True, False)
        # Set user to null
        data = b'{"host": "www.google.com", "user": null}'
        match_context = DummyMatchContext(data)
        match_element = json_model_element.get_match_element(self.path, match_context)
        # Line must be parsed:
        self.assertEqual(2, len(match_element.children))
        self.assertEqual(b"www.google.com", match_element.children[0].get_match_object())
        self.assertEqual(b"", match_element.children[1].get_match_object())
