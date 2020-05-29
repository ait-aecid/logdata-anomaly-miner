import unittest
from aminer.parsing.ParserMatch import ParserMatch
from aminer.parsing.MatchElement import MatchElement


class ParserMatchTest(unittest.TestCase):

    def test1get_match_dictionary(self):
        """This test case checks if all elements are found in the dictionary."""
        a3 = MatchElement('a3', b'a3', b'a3', [])
        a2 = MatchElement('a2', b'a2', b'a2', [a3])
        a1 = MatchElement('a1', b'a1', b'a1', [a2])
        b3 = MatchElement('b3', b'b3', b'b3', [])
        b2 = MatchElement('b2', b'b2', b'b2', [b3])
        b1 = MatchElement('b1', b'b1', b'b1', [b2])

        root_element = MatchElement('root', b'root', b'root', [a1, b1])

        parser_match = ParserMatch(root_element, None)
        dictionary = parser_match.get_match_dictionary()

        self.assertEqual(dictionary['root'], root_element)
        self.assertEqual(dictionary['a1'], a1)
        self.assertEqual(dictionary['a2'], a2)
        self.assertEqual(dictionary['a3'], a3)
        self.assertEqual(dictionary['b1'], b1)
        self.assertEqual(dictionary['b2'], b2)
        self.assertEqual(dictionary['b3'], b3)

    def test2get_match_dictionary_with_match_element_none(self):
        """This test case checks if an Exception is thrown, when a wrong type is used."""
        a3 = MatchElement('a3', b'a3', b'a3', [None])
        a2 = MatchElement('a2', b'a2', b'a2', [a3])
        a1 = MatchElement('a1', b'a1', b'a1', [a2])
        b3 = MatchElement('b3', b'b3', b'b3', [None])
        b2 = MatchElement('b2', b'b2', b'b2', [b3])
        b1 = MatchElement('b1', b'b1', b'b1', [b2])

        root_element = MatchElement('root', b'root', b'root', [a1, b1])

        parser_match = ParserMatch(root_element, None)
        self.assertRaises(AttributeError, parser_match.get_match_dictionary)


if __name__ == "__main__":
    unittest.main()
