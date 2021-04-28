import unittest
from aminer.parsing.FixedWordlistDataModelElement import FixedWordlistDataModelElement
from unit.TestBase import TestBase, DummyMatchContext


class FixedWordlistDataModelElementTest(TestBase):
    """Unittests for the FixedWordlistDataModelElement."""

    id_ = "wordlist"
    path = "path"
    wordlist = [b"wordlist", b"word"]

    def test1get_id(self):
        """Test if get_id works properly."""
        fixed_wordlist_dme = FixedWordlistDataModelElement(self.id_, self.wordlist)
        self.assertEqual(fixed_wordlist_dme.get_id(), self.id_)

    def test2get_child_elements(self):
        """Test if get_child_elements returns None."""
        fixed_wordlist_dme = FixedWordlistDataModelElement(self.id_, self.wordlist)
        self.assertEqual(fixed_wordlist_dme.get_child_elements(), None)

    def test3get_match_element_valid_match(self):
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

    def test4get_match_element_no_match(self):
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

    def test5element_id_input_validation(self):
        """Check if element_id is validated."""
        # empty element_id
        element_id = ""
        self.assertRaises(ValueError, FixedWordlistDataModelElement, element_id, self.wordlist)

        # None element_id
        element_id = None
        self.assertRaises(TypeError, FixedWordlistDataModelElement, element_id, self.wordlist)

        # bytes element_id is not allowed
        element_id = b"path"
        self.assertRaises(TypeError, FixedWordlistDataModelElement, element_id, self.wordlist)

        # boolean element_id is not allowed
        element_id = True
        self.assertRaises(TypeError, FixedWordlistDataModelElement, element_id, self.wordlist)

        # integer element_id is not allowed
        element_id = 123
        self.assertRaises(TypeError, FixedWordlistDataModelElement, element_id, self.wordlist)

        # float element_id is not allowed
        element_id = 123.22
        self.assertRaises(TypeError, FixedWordlistDataModelElement, element_id, self.wordlist)

        # dict element_id is not allowed
        element_id = {"id": "path"}
        self.assertRaises(TypeError, FixedWordlistDataModelElement, element_id, self.wordlist)

        # list element_id is not allowed
        element_id = ["path"]
        self.assertRaises(TypeError, FixedWordlistDataModelElement, element_id, self.wordlist)

        # empty list element_id is not allowed
        element_id = []
        self.assertRaises(TypeError, FixedWordlistDataModelElement, element_id, self.wordlist)

        # empty tuple element_id is not allowed
        element_id = ()
        self.assertRaises(TypeError, FixedWordlistDataModelElement, element_id, self.wordlist)

        # empty set element_id is not allowed
        element_id = set()
        self.assertRaises(TypeError, FixedWordlistDataModelElement, element_id, self.wordlist)

    def test6wordlist_input_validation(self):
        """Check if wordlist is validated."""
        # string wordlist
        wordlist = "path"
        self.assertRaises(TypeError, FixedWordlistDataModelElement, self.id_, wordlist)

        # None wordlist
        wordlist = None
        self.assertRaises(TypeError, FixedWordlistDataModelElement, self.id_, wordlist)

        # bytes wordlist is not allowed
        wordlist = b"path"
        self.assertRaises(TypeError, FixedWordlistDataModelElement, self.id_, wordlist)

        # boolean wordlist is not allowed
        wordlist = True
        self.assertRaises(TypeError, FixedWordlistDataModelElement, self.id_, wordlist)

        # integer wordlist is not allowed
        wordlist = 123
        self.assertRaises(TypeError, FixedWordlistDataModelElement, self.id_, wordlist)

        # float wordlist is not allowed
        wordlist = 123.22
        self.assertRaises(TypeError, FixedWordlistDataModelElement, self.id_, wordlist)

        # dict wordlist is not allowed
        wordlist = {"id": "path"}
        self.assertRaises(TypeError, FixedWordlistDataModelElement, self.id_, wordlist)

        # list wordlist with strings is not allowed
        wordlist = ["path", "path2"]
        self.assertRaises(TypeError, FixedWordlistDataModelElement, self.id_, wordlist)

        # wrong word order
        wordlist = [b"word", b"path", b"path-like"]
        self.assertRaises(ValueError, FixedWordlistDataModelElement, self.id_, wordlist)

        # wrong word order
        wordlist = [b"wordlist", b"word", b"word dictionary"]
        self.assertRaises(ValueError, FixedWordlistDataModelElement, self.id_, wordlist)

        # empty list wordlist is not allowed
        wordlist = []
        self.assertRaises(ValueError, FixedWordlistDataModelElement, self.id_, wordlist)

        # empty tuple wordlist is not allowed
        wordlist = ()
        self.assertRaises(TypeError, FixedWordlistDataModelElement, self.id_, wordlist)

        # empty set wordlist is not allowed
        wordlist = set()
        self.assertRaises(TypeError, FixedWordlistDataModelElement, self.id_, wordlist)

    def test7get_match_element_match_context_input_validation(self):
        """Check if an exception is raised, when other classes than MatchContext are used in get_match_element."""
        model_element = FixedWordlistDataModelElement(self.id_, self.wordlist)
        data = b"abcdefghijklmnopqrstuvwxyz.!?"
        model_element.get_match_element(self.path, DummyMatchContext(data))
        from aminer.parsing.MatchContext import MatchContext
        model_element.get_match_element(self.path, MatchContext(data))

        from aminer.parsing.MatchElement import MatchElement
        self.assertRaises(AttributeError, model_element.get_match_element, self.path, MatchElement(data, None, None, None))
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
