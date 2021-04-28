import unittest
from aminer.parsing.ParserMatch import ParserMatch
from aminer.parsing.MatchElement import MatchElement
from unit.TestBase import TestBase


class ParserMatchTest(TestBase):
    """Unittests for the ParserMatch."""

    match_element = MatchElement("path", b"match_string", b"match_object", None)

    def test1get_match_element(self):
        """Test if get_match_element works properly."""
        match = ParserMatch(self.match_element)
        self.assertEqual(match.get_match_element(), self.match_element)

    def test2get_match_dictionary(self):
        """Test if MatchElements with and without children are evaluated properly and if multiple calls are handled properly."""
        a3 = MatchElement("a3", b"a3", b"a3", None)
        a2 = MatchElement("a2", b"a2", b"a2", [a3])
        a1 = MatchElement("a1", b"a1", b"a1", [a2])
        b3 = MatchElement("b3", b"b3", b"b3", None)
        b2 = MatchElement("b2", b"b2", b"b2", [b3])
        b1 = MatchElement("b1", b"b1", b"b1", [b2])
        root_element = MatchElement("root", b"root", b"root", [a1, b1])

        parser_match = ParserMatch(root_element)
        dictionary = parser_match.get_match_dictionary()

        self.assertEqual(dictionary["root"], root_element)
        self.assertEqual(dictionary["a1"], a1)
        self.assertEqual(dictionary["a2"], a2)
        self.assertEqual(dictionary["a3"], a3)
        self.assertEqual(dictionary["b1"], b1)
        self.assertEqual(dictionary["b2"], b2)
        self.assertEqual(dictionary["b3"], b3)

    def test3match_element_input_validation(self):
        """Check if element_id is validated."""
        self.assertRaises(TypeError, ParserMatch, "string")
        self.assertRaises(TypeError, ParserMatch, None)
        self.assertRaises(TypeError, ParserMatch, b"path")
        self.assertRaises(TypeError, ParserMatch, 123)
        self.assertRaises(TypeError, ParserMatch, 123.22)
        self.assertRaises(TypeError, ParserMatch, True)
        self.assertRaises(TypeError, ParserMatch, {"id": "path"})
        self.assertRaises(TypeError, ParserMatch, ["path"])
        self.assertRaises(TypeError, ParserMatch, [])
        self.assertRaises(TypeError, ParserMatch, ())
        self.assertRaises(TypeError, ParserMatch, set())


if __name__ == "__main__":
    unittest.main()
