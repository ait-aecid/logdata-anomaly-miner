import unittest
from aminer.parsing.FixedWordlistDataModelElement import FixedWordlistDataModelElement
from aminer.parsing.MatchContext import MatchContext
from aminer.parsing.MatchElement import MatchElement
from unit.TestBase import TestBase, DummyMatchContext


class FixedWordlistDataModelElementTest(TestBase):
    """Unittests for the FixedWordlistDataModelElement."""

    id_ = "wordlist"
    path = "path"
    wordlist = [b"wordlist", b"word"]

    def test1get_match_element_valid_match(self):
        """Parse matching substring from MatchContext and check if the MatchContext was updated with all characters."""
        data = b"wordlist, word"
        index = 0
        value = b"wordlist"
        match_context = DummyMatchContext(data)
        fixed_wordlist_dme = FixedWordlistDataModelElement(self.id_, self.wordlist)
        match_element = fixed_wordlist_dme.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, value, index, None)

        data = b"word, wordlist"
        index = 1
        value = b"word"
        match_context = DummyMatchContext(data)
        fixed_wordlist_dme = FixedWordlistDataModelElement(self.id_, self.wordlist)
        match_element = fixed_wordlist_dme.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, value, index, None)

    def test2get_match_element_no_match(self):
        """Parse not matching substring from MatchContext and check if the MatchContext was not changed."""
        data = b"string wordlist"
        match_context = DummyMatchContext(data)
        fixed_wordlist_dme = FixedWordlistDataModelElement(self.id_, self.wordlist)
        match_element = fixed_wordlist_dme.get_match_element(self.path, match_context)
        self.compare_no_match_results(data, match_element, match_context)

        data = b"wor wordlist"
        match_context = DummyMatchContext(data)
        fixed_wordlist_dme = FixedWordlistDataModelElement(self.id_, self.wordlist)
        match_element = fixed_wordlist_dme.get_match_element(self.path, match_context)
        self.compare_no_match_results(data, match_element, match_context)

        data = b"0 wordlist"
        match_context = DummyMatchContext(data)
        fixed_wordlist_dme = FixedWordlistDataModelElement(self.id_, self.wordlist)
        match_element = fixed_wordlist_dme.get_match_element(self.path, match_context)
        self.compare_no_match_results(data, match_element, match_context)

        data = b"1 word"
        match_context = DummyMatchContext(data)
        fixed_wordlist_dme = FixedWordlistDataModelElement(self.id_, self.wordlist)
        match_element = fixed_wordlist_dme.get_match_element(self.path, match_context)
        self.compare_no_match_results(data, match_element, match_context)

    def test3element_id_input_validation(self):
        """Check if element_id is validated."""
        self.assertRaises(ValueError, FixedWordlistDataModelElement, "", self.wordlist)  # empty element_id
        self.assertRaises(TypeError, FixedWordlistDataModelElement, None, self.wordlist)  # None element_id
        self.assertRaises(TypeError, FixedWordlistDataModelElement, b"path", self.wordlist)  # bytes element_id is not allowed
        self.assertRaises(TypeError, FixedWordlistDataModelElement, True, self.wordlist)  # boolean element_id is not allowed
        self.assertRaises(TypeError, FixedWordlistDataModelElement, 123, self.wordlist)  # integer element_id is not allowed
        self.assertRaises(TypeError, FixedWordlistDataModelElement, 123.22, self.wordlist)  # float element_id is not allowed
        self.assertRaises(TypeError, FixedWordlistDataModelElement, {"id": "path"}, self.wordlist)  # dict element_id is not allowed
        self.assertRaises(TypeError, FixedWordlistDataModelElement, ["path"], self.wordlist)  # list element_id is not allowed
        self.assertRaises(TypeError, FixedWordlistDataModelElement, [], self.wordlist)  # empty list element_id is not allowed
        self.assertRaises(TypeError, FixedWordlistDataModelElement, (), self.wordlist)  # empty tuple element_id is not allowed
        self.assertRaises(TypeError, FixedWordlistDataModelElement, set(), self.wordlist)  # empty set element_id is not allowed

    def test4wordlist_input_validation(self):
        """Check if wordlist is validated."""
        self.assertRaises(TypeError, FixedWordlistDataModelElement, self.id_, "path")  # string wordlist
        self.assertRaises(TypeError, FixedWordlistDataModelElement, self.id_, None)  # None wordlist
        self.assertRaises(TypeError, FixedWordlistDataModelElement, self.id_, b"path")  # bytes wordlist is not allowed
        self.assertRaises(TypeError, FixedWordlistDataModelElement, self.id_, True)  # boolean wordlist is not allowed
        self.assertRaises(TypeError, FixedWordlistDataModelElement, self.id_, 123)  # integer wordlist is not allowed
        self.assertRaises(TypeError, FixedWordlistDataModelElement, self.id_, 123.22)  # float wordlist is not allowed
        self.assertRaises(TypeError, FixedWordlistDataModelElement, self.id_, {"id": "path"})  # dict wordlist is not allowed
        self.assertRaises(TypeError, FixedWordlistDataModelElement, self.id_, ["path", "path2"])  # list wordlist with strings not allowed
        self.assertRaises(ValueError, FixedWordlistDataModelElement, self.id_, [b"word", b"path", b"path-like"])  # wrong word order
        self.assertRaises(ValueError, FixedWordlistDataModelElement, self.id_, [b"wordlist", b"word", b"word dictionary"])  # wrong order
        self.assertRaises(ValueError, FixedWordlistDataModelElement, self.id_, [])  # empty list wordlist is not allowed
        self.assertRaises(TypeError, FixedWordlistDataModelElement, self.id_, ())  # empty tuple wordlist is not allowed
        self.assertRaises(TypeError, FixedWordlistDataModelElement, self.id_, set())  # empty set wordlist is not allowed

    def test5get_match_element_match_context_input_validation(self):
        """Check if an exception is raised, when other classes than MatchContext are used in get_match_element."""
        model_element = FixedWordlistDataModelElement(self.id_, self.wordlist)
        data = b"abcdefghijklmnopqrstuvwxyz.!?"
        model_element.get_match_element(self.path, DummyMatchContext(data))
        model_element.get_match_element(self.path, MatchContext(data))

        self.assertRaises(AttributeError, model_element.get_match_element, self.path, MatchElement(None, data, None, None))
        self.assertRaises(AttributeError, model_element.get_match_element, self.path, data)
        self.assertRaises(AttributeError, model_element.get_match_element, self.path, data.decode())
        self.assertRaises(AttributeError, model_element.get_match_element, self.path, 123)
        self.assertRaises(AttributeError, model_element.get_match_element, self.path, 123.22)
        self.assertRaises(AttributeError, model_element.get_match_element, self.path, True)
        self.assertRaises(AttributeError, model_element.get_match_element, self.path, None)
        self.assertRaises(AttributeError, model_element.get_match_element, self.path, [])
        self.assertRaises(AttributeError, model_element.get_match_element, self.path, {"key": MatchContext(data)})
        self.assertRaises(AttributeError, model_element.get_match_element, self.path, set())
        self.assertRaises(AttributeError, model_element.get_match_element, self.path, ())
        self.assertRaises(AttributeError, model_element.get_match_element, self.path, model_element)


if __name__ == "__main__":
    unittest.main()
