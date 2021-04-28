import unittest
from aminer.parsing.MatchContext import MatchContext
from aminer.parsing.MatchElement import MatchElement
from aminer.parsing.ElementValueBranchModelElement import ElementValueBranchModelElement
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
        element_value_branch_me = ElementValueBranchModelElement(
            self.id_, self.value_model, None, {"path: ": self.path_me, "data: ": self.data_me})
        data = b"path: /model"
        match_context = DummyMatchContext(data)
        match_element = element_value_branch_me.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, data, data, [
            MatchElement("path/value_branch/branch/path", self.path_path, self.path_path, None),
            MatchElement("path/value_branch/value_model", self.path_fixed_string, self.path_fixed_string, None)])

        data = b"data: this is some random data: 255."
        match_context = DummyMatchContext(data)
        match_element = element_value_branch_me.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, data, data, [
            MatchElement("path/value_branch/branch/data", self.data_path, self.data_path, None),
            MatchElement("path/value_branch/value_model", self.data_fixed_string, self.data_fixed_string, None)])

    def test4get_match_element_no_match(self):
        """Parse not matching substring from MatchContext and check if the MatchContext was not changed."""
        element_value_branch_me = ElementValueBranchModelElement(
            self.id_, self.value_model, None, {"path: ": self.path_me, "data: ": self.data_me})
        data = b"path: /random"
        match_context = DummyMatchContext(data)
        match_element = element_value_branch_me.get_match_element(self.path, match_context)
        self.compare_no_match_results(data, match_element, match_context)

        data = b"path: this is some random data: 255."
        match_context = DummyMatchContext(data)
        match_element = element_value_branch_me.get_match_element(self.path, match_context)
        self.compare_no_match_results(data, match_element, match_context)

        data = b"data: /model"
        match_context = DummyMatchContext(data)
        match_element = element_value_branch_me.get_match_element(self.path, match_context)
        self.compare_no_match_results(data, match_element, match_context)

        data = b"path: "
        match_context = DummyMatchContext(data)
        match_element = element_value_branch_me.get_match_element(self.path, match_context)
        self.compare_no_match_results(data, match_element, match_context)

        data = b"data: "
        match_context = DummyMatchContext(data)
        match_element = element_value_branch_me.get_match_element(self.path, match_context)
        self.compare_no_match_results(data, match_element, match_context)

    def test5element_id_input_validation(self):
        """Check if element_id is validated."""
        branch_model_dict = {"path: ": self.path_me, "data: ": self.data_me}
        self.assertRaises(ValueError, ElementValueBranchModelElement, "", self.value_model, None, branch_model_dict)
        self.assertRaises(TypeError, ElementValueBranchModelElement, None, self.value_model, None, branch_model_dict)
        self.assertRaises(TypeError, ElementValueBranchModelElement, b"path", self.value_model, None, branch_model_dict)
        self.assertRaises(TypeError, ElementValueBranchModelElement, True, self.value_model, None, branch_model_dict)
        self.assertRaises(TypeError, ElementValueBranchModelElement, 123, self.value_model, None, branch_model_dict)
        self.assertRaises(TypeError, ElementValueBranchModelElement, 123.22, self.value_model, None, branch_model_dict)
        self.assertRaises(TypeError, ElementValueBranchModelElement, {"id": "path"}, self.value_model, None, branch_model_dict)
        self.assertRaises(TypeError, ElementValueBranchModelElement, ["path"], self.value_model, None, branch_model_dict)
        self.assertRaises(TypeError, ElementValueBranchModelElement, [], self.value_model, None, branch_model_dict)
        self.assertRaises(TypeError, ElementValueBranchModelElement, (), self.value_model, None, branch_model_dict)
        self.assertRaises(TypeError, ElementValueBranchModelElement, set(), self.value_model, None, branch_model_dict)

    def test6value_model_input_validation(self):
        """Check if value_model is validated."""
        branch_model_dict = {"path: ": self.path_me, "data: ": self.data_me}
        self.assertRaises(TypeError, ElementValueBranchModelElement, self.id_, "path", None, branch_model_dict)
        self.assertRaises(TypeError, ElementValueBranchModelElement, self.id_, None, None, branch_model_dict)
        self.assertRaises(TypeError, ElementValueBranchModelElement, self.id_, b"path", None, branch_model_dict)
        self.assertRaises(TypeError, ElementValueBranchModelElement, self.id_, True, None, branch_model_dict)
        self.assertRaises(TypeError, ElementValueBranchModelElement, self.id_, 123, None, branch_model_dict)
        self.assertRaises(TypeError, ElementValueBranchModelElement, self.id_, 123.22, None, branch_model_dict)
        self.assertRaises(TypeError, ElementValueBranchModelElement, self.id_, True, None, branch_model_dict)
        self.assertRaises(TypeError, ElementValueBranchModelElement, self.id_, {"id": "path"}, None, branch_model_dict)
        self.assertRaises(TypeError, ElementValueBranchModelElement, self.id_, ["path"], None, branch_model_dict)
        self.assertRaises(TypeError, ElementValueBranchModelElement, self.id_, [], None, branch_model_dict)
        self.assertRaises(TypeError, ElementValueBranchModelElement, self.id_, (), None, branch_model_dict)
        self.assertRaises(TypeError, ElementValueBranchModelElement, self.id_, set(), None, branch_model_dict)

    def test7value_path_input_validation(self):
        """Check if value_path is validated."""
        branch_model_dict = {"path: ": self.path_me, "data: ": self.data_me}
        self.assertRaises(ValueError, ElementValueBranchModelElement, self.id_, self.value_model, "", branch_model_dict)
        self.assertRaises(TypeError, ElementValueBranchModelElement, self.id_, self.value_model, b"path", branch_model_dict)
        self.assertRaises(TypeError, ElementValueBranchModelElement, self.id_, self.value_model, True, branch_model_dict)
        self.assertRaises(TypeError, ElementValueBranchModelElement, self.id_, self.value_model, 123, branch_model_dict)
        self.assertRaises(TypeError, ElementValueBranchModelElement, self.id_, self.value_model, 123.22, branch_model_dict)
        self.assertRaises(TypeError, ElementValueBranchModelElement, self.id_, self.value_model, {"id": "path"}, branch_model_dict)
        self.assertRaises(TypeError, ElementValueBranchModelElement, self.id_, self.value_model, ["path"], branch_model_dict)
        self.assertRaises(TypeError, ElementValueBranchModelElement, self.id_, self.value_model, [], branch_model_dict)
        self.assertRaises(TypeError, ElementValueBranchModelElement, self.id_, self.value_model, (), branch_model_dict)
        self.assertRaises(TypeError, ElementValueBranchModelElement, self.id_, self.value_model, set(), branch_model_dict)

    def test8branch_model_dict_input_validation(self):
        """Check if value_path is validated."""
        self.assertRaises(TypeError, ElementValueBranchModelElement, self.id_, self.value_model, None, "path")
        self.assertRaises(TypeError, ElementValueBranchModelElement, self.id_, self.value_model, None, None)
        self.assertRaises(TypeError, ElementValueBranchModelElement, self.id_, self.value_model, None, b"path")
        self.assertRaises(TypeError, ElementValueBranchModelElement, self.id_, self.value_model, None, True)
        self.assertRaises(TypeError, ElementValueBranchModelElement, self.id_, self.value_model, None, 123)
        self.assertRaises(TypeError, ElementValueBranchModelElement, self.id_, self.value_model, None, 123.22)
        # dict branch_model_dict without ModelElementInterface values is not allowed
        self.assertRaises(TypeError, ElementValueBranchModelElement, self.id_, self.value_model, None, {"id": "path"})
        self.assertRaises(TypeError, ElementValueBranchModelElement, self.id_, self.value_model, None, ["path"])
        self.assertRaises(TypeError, ElementValueBranchModelElement, self.id_, self.value_model, None, [])
        self.assertRaises(TypeError, ElementValueBranchModelElement, self.id_, self.value_model, None, ())
        self.assertRaises(TypeError, ElementValueBranchModelElement, branch_model_dict, self.value_model, None, set())

    def test9default_branch_input_validation(self):
        """Check if value_path is validated."""
        branch_model_dict = {"path: ": self.path_me, "data: ": self.data_me}
        self.assertRaises(TypeError, ElementValueBranchModelElement, self.id_, self.value_model, None, branch_model_dict, "path")
        self.assertRaises(TypeError, ElementValueBranchModelElement, self.id_, self.value_model, None, branch_model_dict, b"path")
        self.assertRaises(TypeError, ElementValueBranchModelElement, self.id_, self.value_model, None, branch_model_dict, True)
        self.assertRaises(TypeError, ElementValueBranchModelElement, self.id_, self.value_model, None, branch_model_dict, 123)
        self.assertRaises(TypeError, ElementValueBranchModelElement, self.id_, self.value_model, None, branch_model_dict, 123.22)
        self.assertRaises(TypeError, ElementValueBranchModelElement, self.id_, self.value_model, None, branch_model_dict, {"id": "path"})
        self.assertRaises(TypeError, ElementValueBranchModelElement, self.id_, self.value_model, None, branch_model_dict, ["path"])
        self.assertRaises(TypeError, ElementValueBranchModelElement, self.id_, self.value_model, None, branch_model_dict, [])
        self.assertRaises(TypeError, ElementValueBranchModelElement, self.id_, self.value_model, None, branch_model_dict, ())
        self.assertRaises(TypeError, ElementValueBranchModelElement, self.id_, self.value_model, None, branch_model_dict, set())

    def test10get_match_element_match_context_input_validation(self):
        """Check if an exception is raised, when other classes than MatchContext are used in get_match_element."""
        model_element = ElementValueBranchModelElement(self.id_, self.value_model, None, {"path: ": self.path_me, "data: ": self.data_me})
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
