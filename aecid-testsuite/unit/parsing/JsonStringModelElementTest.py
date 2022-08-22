import copy
import unittest
import json
from aminer.parsing.JsonStringModelElement import JsonStringModelElement, JsonAccessObject
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


class JsonAccessObjectTest(TestBase):
    
    def test1get_id(self):
        """Parses a dictionary and see if everything is flattened properly"""
        d = {'a': 'b', 'c': {'w': 'g', 'rata': 'mahatta', 'tic': {'tac': 'toe'}, 'brat': ['worst','wuast',{'key': ['wurst','fleisch'], 'food': 'veggie'},'blues'],'bist': 'narrisch'}, 'foo': 'bar'}
        """
        a: b
        c.w: g
        c.rata: mahatta
        c.tic.tac: toe
        c.brat[0]: worst
        c.brat[1]: wuast
        c.brat[2].key[0]: wurst
        c.brat[2].key[1]: fleisch
        c.brat[2].food: veggie
        c.brat[3]: blues
        foo: bar
        """
        jao =  JsonAccessObject(d)
        self.assertTrue(jao.collection['a'])
        self.assertTrue(jao.collection['c.w'])
        self.assertTrue(jao.collection['c.rata'])
        self.assertTrue(jao.collection['c.tic.tac'])
        self.assertTrue(jao.collection['c.brat[0]'])
        self.assertTrue(jao.collection['c.brat[1]'])
        self.assertTrue(jao.collection['c.brat[2].key[0]'])
        self.assertTrue(jao.collection['c.brat[2].key[1]'])
        self.assertTrue(jao.collection['c.brat[2].food'])
        self.assertTrue(jao.collection['c.brat[3]'])
        self.assertTrue(jao.collection['c.bist'])
        self.assertTrue(jao.collection['foo'])
        self.assertEqual(12,len(jao.collection))
        self.assertEqual("b",jao.collection["a"]["value"])
        self.assertEqual("g",jao.collection["c.w"]["value"])
        self.assertEqual("mahatta",jao.collection["c.rata"]["value"])
        self.assertEqual("toe",jao.collection["c.tic.tac"]["value"])
        self.assertEqual("worst",jao.collection["c.brat[0]"]["value"])
        self.assertEqual("wuast",jao.collection["c.brat[1]"]["value"])
        self.assertEqual("wurst",jao.collection["c.brat[2].key[0]"]["value"])
        self.assertEqual("fleisch",jao.collection["c.brat[2].key[1]"]["value"])
        self.assertEqual("veggie",jao.collection["c.brat[2].food"]["value"])
        self.assertEqual("blues",jao.collection["c.brat[3]"]["value"])
        self.assertEqual("bar",jao.collection["foo"]["value"])

