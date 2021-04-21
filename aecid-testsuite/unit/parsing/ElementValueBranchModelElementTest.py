import unittest
from aminer.parsing.MatchContext import MatchContext
from aminer.parsing.MatchElement import MatchElement
from aminer.parsing.ElementValueBranchModelElement import ElementValueBranchModelElement
from aminer.parsing.FixedDataModelElement import FixedDataModelElement
from aminer.parsing.SequenceModelElement import SequenceModelElement
from aminer.parsing.DecimalIntegerValueModelElement import DecimalIntegerValueModelElement
from aminer.parsing.FirstMatchModelElement import FirstMatchModelElement
from aminer.parsing.FixedWordlistDataModelElement import FixedWordlistDataModelElement
from unit.TestBase import TestBase, DummyMatchContext, DummyFixedDataModelElement, DummyFirstMatchModelElement


class ElementValueBranchModelElementTest(TestBase):
    """Unittests for the ElementValueBranchModelElement."""

    id_ = "value_branch"
    path = "path"
    value_path = "value_model"
    path_path = b"path: "
    data_path = b"data: "
    path_fixed_string = b"/model"
    data_fixed_string = b"this is some random data: 255."
    value_model = DummyFirstMatchModelElement(
        "branch", [DummyFixedDataModelElement("path", path_path), DummyFixedDataModelElement("data", data_path)])
    path_me = DummyFixedDataModelElement(value_path, path_fixed_string)
    data_me = DummyFixedDataModelElement(value_path, data_fixed_string)
    children = [value_model, path_me, data_me]

    def test1get_id(self):
        """Test if get_id works properly."""
        element_value_branch_me = ElementValueBranchModelElement(
            self.id_, self.value_model, None, {"path: ": self.path_me, "data: ": self.data_me})
        self.assertEqual(element_value_branch_me.get_id(), self.id_)

    def test2get_child_elements(self):
        """Test if get_child_elements returns None."""
        element_value_branch_me = ElementValueBranchModelElement(
            self.id_, self.value_model, None, {"path: ": self.path_me, "data: ": self.data_me})
        self.assertEqual(element_value_branch_me.get_child_elements(), self.children)

    def test3get_match_element_valid_match(self):
        """Parse matching substring from MatchContext and check if the MatchContext was updated with all characters."""
        data = b"path: /model"
        match_context = DummyMatchContext(data)
        element_value_branch_me = ElementValueBranchModelElement(
            self.id_, self.value_model, None, {"path: ": self.path_me, "data: ": self.data_me})
        match_element = element_value_branch_me.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, data, data, [
            MatchElement("path/value_branch/branch/path", self.path_path, self.path_path, None),
            MatchElement("path/value_branch/value_model", self.path_fixed_string, self.path_fixed_string, None)])

    def test4get_match_element_no_match(self):
        """Parse not matching substring from MatchContext and check if the MatchContext was not changed."""
        data = b"path: /random"
        match_context = DummyMatchContext(data)
        element_value_branch_me = ElementValueBranchModelElement(
            self.id_, self.value_model, None, {"path: ": self.path_me, "data: ": self.data_me})
        match_element = element_value_branch_me.get_match_element(self.path, match_context)
        self.compare_no_match_results(data, match_element, match_context)

    def test5element_id_input_validation(self):
        """Check if element_id is validated."""
        branch_model_dict = {"path: ": self.path_me, "data: ": self.data_me}
        # empty element_id
        element_id = ""
        self.assertRaises(ValueError, ElementValueBranchModelElement, element_id, self.value_model, None, branch_model_dict)

        # None element_id
        element_id = None
        self.assertRaises(TypeError, ElementValueBranchModelElement, element_id, self.value_model, None, branch_model_dict)

        # bytes element_id is not allowed
        element_id = b"path"
        self.assertRaises(TypeError, ElementValueBranchModelElement, element_id, self.value_model, None, branch_model_dict)

        # bytes element_id is not allowed
        element_id = True
        self.assertRaises(TypeError, ElementValueBranchModelElement, element_id, self.value_model, None, branch_model_dict)

        # integer element_id is not allowed
        element_id = 123
        self.assertRaises(TypeError, ElementValueBranchModelElement, element_id, self.value_model, None, branch_model_dict)

        # float element_id is not allowed
        element_id = 123.22
        self.assertRaises(TypeError, ElementValueBranchModelElement, element_id, self.value_model, None, branch_model_dict)

        # boolean element_id is not allowed
        element_id = True
        self.assertRaises(TypeError, ElementValueBranchModelElement, element_id, self.value_model, None, branch_model_dict)

        # dict element_id is not allowed
        element_id = {"id": "path"}
        self.assertRaises(TypeError, ElementValueBranchModelElement, element_id, self.value_model, None, branch_model_dict)

        # list element_id is not allowed
        element_id = ["path"]
        self.assertRaises(TypeError, ElementValueBranchModelElement, element_id, self.value_model, None, branch_model_dict)

        # empty list element_id is not allowed
        element_id = []
        self.assertRaises(TypeError, ElementValueBranchModelElement, element_id, self.value_model, None, branch_model_dict)

        # empty tuple element_id is not allowed
        element_id = ()
        self.assertRaises(TypeError, ElementValueBranchModelElement, element_id, self.value_model, None, branch_model_dict)

        # empty set element_id is not allowed
        element_id = set()
        self.assertRaises(TypeError, ElementValueBranchModelElement, element_id, self.value_model, None, branch_model_dict)

    def test6get_match_element_match_context_input_validation(self):
        """Check if an exception is raised, when other classes than MatchContext are used in get_match_element."""
        model_element = ElementValueBranchModelElement(self.id_, self.value_model, None, {"path: ": self.path_me, "data: ": self.data_me})
        data = b'abcdefghijklmnopqrstuvwxyz.!?'
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














    # match = b'match '
    # fixed_string = b'fixed String'
    # path_to_match = b'match path: /path/to/match'
    # match_data = b'match data: 25000'
    # match_string = b'match string: fixed String'
    # string_path_to_match = b'match string: /path/to/match'
    #
    # fixed_data_me1 = FixedDataModelElement("fixed 1", match)
    # fixed_data_me2 = FixedDataModelElement("fixed 2", fixed_string)
    # fixed_wordlist_data_model_element = FixedWordlistDataModelElement("wordlist", [b'data: ', b'string: '])
    # decimal_integer_value_model_element = DecimalIntegerValueModelElement("decimal")
    # seq1 = SequenceModelElement("seq1", [fixed_data_me1, fixed_wordlist_data_model_element])
    # seq2 = SequenceModelElement("seq2", [fixed_data_me1, fixed_wordlist_data_model_element, fixed_data_me2])
    # first_match_me = FirstMatchModelElement("first", [seq1, seq2])
    # fixed_data_me3 = FixedDataModelElement("fixed 3", path_to_match)
    #
    # def test1_match_element_found(self):
    #     """In this test case different possible parameters are used to obtain a MatchElement successfully."""
    #     match_context = MatchContext(self.match_data)
    #     element_value_branch_model_element = ElementValueBranchModelElement(
    #         "id", self.first_match_me, "wordlist", {0: self.decimal_integer_value_model_element, 1: self.fixed_data_me2})
    #     match_element = element_value_branch_model_element.get_match_element("elementValueBranchME match", match_context)
    #     self.assertEqual(match_element.get_path(), 'elementValueBranchME match/id')
    #     self.assertEqual(match_element.get_match_string(), self.match_data)
    #     self.assertEqual(match_element.get_match_object(), self.match_data)
    #     self.assertEqual(match_element.get_children()[0].get_path(), 'elementValueBranchME match/id/first/seq1')
    #     self.assertEqual(match_element.get_children()[0].get_match_string(), b'match data: ')
    #     self.assertEqual(match_element.get_children()[0].get_match_object(), b'match data: ')
    #     self.assertEqual(match_element.get_children()[0].get_children()[0].get_path(), 'elementValueBranchME match/id/first/seq1/fixed 1')
    #     self.assertEqual(match_element.get_children()[0].get_children()[0].get_match_string(), self.match)
    #     self.assertEqual(match_element.get_children()[0].get_children()[0].get_match_object(), self.match)
    #     self.assertEqual(match_element.get_children()[0].get_children()[0].get_children(), None)
    #     self.assertEqual(match_element.get_children()[0].get_children()[1].get_path(), 'elementValueBranchME match/id/first/seq1/wordlist')
    #     self.assertEqual(match_element.get_children()[0].get_children()[1].get_match_string(), b'data: ')
    #     self.assertEqual(match_element.get_children()[0].get_children()[1].get_match_object(), 0)
    #     self.assertEqual(match_element.get_children()[0].get_children()[1].get_children(), None)
    #     self.assertEqual(match_element.get_children()[1].get_path(), 'elementValueBranchME match/id/decimal')
    #     self.assertEqual(match_element.get_children()[1].get_match_string(), b'25000')
    #     self.assertEqual(match_element.get_children()[1].get_match_object(), 25000)
    #     self.assertEqual(match_element.get_children()[1].get_children(), None)
    #
    #     match_context = MatchContext(self.match_string)
    #     match_element = element_value_branch_model_element.get_match_element("elementValueBranchME match", match_context)
    #     self.assertEqual(match_element.get_path(), 'elementValueBranchME match/id')
    #     self.assertEqual(match_element.get_match_string(), self.match_string)
    #     self.assertEqual(match_element.get_match_object(), self.match_string)
    #     self.assertEqual(match_element.get_children()[0].get_path(), 'elementValueBranchME match/id/first/seq1')
    #     self.assertEqual(match_element.get_children()[0].get_match_string(), b'match string: ')
    #     self.assertEqual(match_element.get_children()[0].get_match_object(), b'match string: ')
    #     self.assertEqual(match_element.get_children()[0].get_children()[0].get_path(), 'elementValueBranchME match/id/first/seq1/fixed 1')
    #     self.assertEqual(match_element.get_children()[0].get_children()[0].get_match_string(), self.match)
    #     self.assertEqual(match_element.get_children()[0].get_children()[0].get_match_object(), self.match)
    #     self.assertEqual(match_element.get_children()[0].get_children()[0].get_children(), None)
    #     self.assertEqual(match_element.get_children()[0].get_children()[1].get_path(), 'elementValueBranchME match/id/first/seq1/wordlist')
    #     self.assertEqual(match_element.get_children()[0].get_children()[1].get_match_string(), b'string: ')
    #     self.assertEqual(match_element.get_children()[0].get_children()[1].get_match_object(), 1)
    #     self.assertEqual(match_element.get_children()[0].get_children()[1].get_children(), None)
    #     self.assertEqual(match_element.get_children()[1].get_path(), 'elementValueBranchME match/id/fixed 2')
    #     self.assertEqual(match_element.get_children()[1].get_match_string(), self.fixed_string)
    #     self.assertEqual(match_element.get_children()[1].get_match_object(), self.fixed_string)
    #     self.assertEqual(match_element.get_children()[1].get_children(), None)
    #
    # def test2_match_element_not_found(self):
    #     """In this test case all possible ways of not getting a MatchElement successfully are tested."""
    #     # no modelMatch
    #     element_value_branch_model_element = ElementValueBranchModelElement(
    #         "id", self.first_match_me, "wordlist", {0: self.decimal_integer_value_model_element, 1: self.fixed_data_me2})
    #     match_context = MatchContext(self.path_to_match)
    #     self.assertEqual(element_value_branch_model_element.get_match_element('match', match_context), None)
    #     self.assertEqual(match_context.match_data, self.path_to_match)
    #
    #     # no matchChildren
    #     element_value_branch_model_element = ElementValueBranchModelElement(
    #         "id", self.fixed_data_me3, "wordlist", {0: self.decimal_integer_value_model_element, 1: self.fixed_data_me2})
    #     match_context = MatchContext(self.path_to_match)
    #     self.assertEqual(element_value_branch_model_element.get_match_element('match', match_context), None)
    #     self.assertEqual(match_context.match_data, self.path_to_match)
    #
    #     # no branchModel
    #     element_value_branch_model_element = ElementValueBranchModelElement(
    #         "id", self.first_match_me, "wordlist", {0: self.decimal_integer_value_model_element})
    #     match_context = MatchContext(self.string_path_to_match)
    #     self.assertEqual(element_value_branch_model_element.get_match_element('match', match_context), None)
    #     self.assertEqual(match_context.match_data, self.string_path_to_match)
    #
    #     # no branchMatch
    #     element_value_branch_model_element = ElementValueBranchModelElement(
    #         "id", self.first_match_me, "wordlist", {0: self.decimal_integer_value_model_element, 1: self.fixed_data_me2})
    #     match_context = MatchContext(self.string_path_to_match)
    #     self.assertEqual(element_value_branch_model_element.get_match_element('match', match_context), None)
    #     self.assertEqual(match_context.match_data, self.string_path_to_match)
    #
    # def test3_get_child_elements(self):
    #     """In this test case the functionality of the get_child_elements-method is tested."""
    #     element_value_branch_model_element = ElementValueBranchModelElement(
    #         "id", self.first_match_me, "wordlist", {0: self.decimal_integer_value_model_element, 1: self.fixed_data_me2})
    #     self.assertEqual(element_value_branch_model_element.get_child_elements(), [
    #         self.first_match_me, self.decimal_integer_value_model_element, self.fixed_data_me2])


if __name__ == "__main__":
    unittest.main()
