import unittest
from aminer.parsing.FixedDataModelElement import FixedDataModelElement
from aminer.parsing.MatchContext import MatchContext
from aminer.parsing.MatchElement import MatchElement
from unit.TestBase import TestBase, DummyMatchContext


class FixedDataModelElementTest(TestBase):
    """Unittests for the FixedDataModelElement."""

    data = b"fixed data. Other data."
    id_ = "fixed"
    path = "path"

    def test1get_match_element_valid_match(self):
        """Parse matching substring from MatchContext and check if the MatchContext was updated with the fixed string."""
        fixed_string = b"fixed data."
        fixed_dme = FixedDataModelElement(self.id_, fixed_string)
        match_context = DummyMatchContext(self.data)
        match_element = fixed_dme.get_match_element(self.path, match_context)
        self.compare_match_results(self.data, match_element, match_context, self.id_, self.path, fixed_string, fixed_string, None)

    def test2get_match_element_no_match(self):
        """Parse not matching substring from MatchContext and check if the MatchContext was not changed."""
        no_match_string = b"Hello World."
        match_context = DummyMatchContext(self.data)
        fixed_dme = FixedDataModelElement(self.id_, no_match_string)
        match_element = fixed_dme.get_match_element(self.path, match_context)
        self.compare_no_match_results(self.data, match_element, match_context)

    def test3element_id_input_validation(self):
        """Check if element_id is validated."""
        self.assertRaises(ValueError, FixedDataModelElement, "", self.data)  # empty element_id
        self.assertRaises(TypeError, FixedDataModelElement, None, self.data)  # None element_id
        self.assertRaises(TypeError, FixedDataModelElement, b"path", self.data)  # bytes element_id is not allowed
        self.assertRaises(TypeError, FixedDataModelElement, True, self.data)  # boolean element_id is not allowed
        self.assertRaises(TypeError, FixedDataModelElement, 123, self.data)  # integer element_id is not allowed
        self.assertRaises(TypeError, FixedDataModelElement, 123.22, self.data)  # float element_id is not allowed
        self.assertRaises(TypeError, FixedDataModelElement, {"id": "path"}, self.data)  # dict element_id is not allowed
        self.assertRaises(TypeError, FixedDataModelElement, ["path"], self.data)  # list element_id is not allowed
        self.assertRaises(TypeError, FixedDataModelElement, [], self.data)  # empty list element_id is not allowed
        self.assertRaises(TypeError, FixedDataModelElement, (), self.data)  # empty tuple element_id is not allowed
        self.assertRaises(TypeError, FixedDataModelElement, set(), self.data)  # empty set element_id is not allowed

    def test4fixed_data_input_validation(self):
        """Check if fixed_data is validated."""
        self.assertRaises(ValueError, FixedDataModelElement, self.id_, b"")  # empty fixed_string
        self.assertRaises(TypeError, FixedDataModelElement, self.id_, None)  # None fixed_string
        self.assertRaises(TypeError, FixedDataModelElement, self.id_, "path")  # string fixed_string is not allowed
        self.assertRaises(TypeError, FixedDataModelElement, self.id_, True)  # boolean fixed_string is not allowed
        self.assertRaises(TypeError, FixedDataModelElement, self.id_, 123)  # integer fixed_string is not allowed
        self.assertRaises(TypeError, FixedDataModelElement, self.id_, 123.22)  # float fixed_string is not allowed
        self.assertRaises(TypeError, FixedDataModelElement, self.id_, {"string": "string"})  # dict fixed_string is not allowed
        self.assertRaises(TypeError, FixedDataModelElement, self.id_, ["path"])  # list fixed_string is not allowed
        self.assertRaises(TypeError, FixedDataModelElement, self.id_, [])  # empty list fixed_string is not allowed
        self.assertRaises(TypeError, FixedDataModelElement, self.id_, ())  # empty tuple fixed_string is not allowed
        self.assertRaises(TypeError, FixedDataModelElement, self.id_, set())  # empty set fixed_string is not allowed

    def test5get_match_element_match_context_input_validation(self):
        """Check if an exception is raised, when other classes than MatchContext are used in get_match_element."""
        model_element = FixedDataModelElement(self.id_, self.data)
        data = self.data
        model_element.get_match_element(self.path, DummyMatchContext(data))
        model_element.get_match_element(self.path, MatchContext(data))

        self.assertRaises(AttributeError, model_element.get_match_element, self.path, MatchElement(self.path, data, None, None))
        self.assertRaises(AttributeError, model_element.get_match_element, self.path, data)
        self.assertRaises(AttributeError, model_element.get_match_element, self.path, data.decode())
        self.assertRaises(AttributeError, model_element.get_match_element, self.path, True)
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
