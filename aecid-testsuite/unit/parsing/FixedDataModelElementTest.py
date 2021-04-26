import unittest
from aminer.parsing.FixedDataModelElement import FixedDataModelElement
from unit.TestBase import TestBase, DummyMatchContext


class FixedDataModelElementTest(TestBase):
    """Unittests for the FixedDataModelElement."""

    data = b"fixed data. Other data."
    id_ = "fixed"
    path = "path"

    def test1get_id(self):
        """Test if get_id works properly."""
        fixed_dme = FixedDataModelElement(self.id_, self.data)
        self.assertEqual(fixed_dme.get_id(), self.id_)

    def test2get_child_elements(self):
        """Test if get_child_elements returns None."""
        fixed_dme = FixedDataModelElement(self.id_, self.data)
        self.assertEqual(fixed_dme.get_child_elements(), None)

    def test3get_match_element_valid_match(self):
        """Parse matching substring from MatchContext and check if the MatchContext was updated with the fixed string."""
        fixed_string = b"fixed data."
        fixed_dme = FixedDataModelElement(self.id_, fixed_string)
        match_context = DummyMatchContext(self.data)
        match_element = fixed_dme.get_match_element(self.path, match_context)
        self.compare_match_results(self.data, match_element, match_context, self.id_, self.path, fixed_string, fixed_string, None)

    def test4get_match_element_no_match(self):
        """Parse not matching substring from MatchContext and check if the MatchContext was not changed."""
        no_match_string = b"Hello World."
        match_context = DummyMatchContext(self.data)
        fixed_dme = FixedDataModelElement(self.id_, no_match_string)
        match_element = fixed_dme.get_match_element(self.path, match_context)
        self.compare_no_match_results(self.data, match_element, match_context)

    def test5element_id_input_validation(self):
        """Check if element_id is validated."""
        # empty element_id
        element_id = ""
        self.assertRaises(ValueError, FixedDataModelElement, element_id, self.data)

        # None element_id
        element_id = None
        self.assertRaises(TypeError, FixedDataModelElement, element_id, self.data)

        # bytes element_id is not allowed
        element_id = b"path"
        self.assertRaises(TypeError, FixedDataModelElement, element_id, self.data)

        # boolean element_id is not allowed
        element_id = True
        self.assertRaises(TypeError, FixedDataModelElement, element_id, self.data)

        # integer element_id is not allowed
        element_id = 123
        self.assertRaises(TypeError, FixedDataModelElement, element_id, self.data)

        # float element_id is not allowed
        element_id = 123.22
        self.assertRaises(TypeError, FixedDataModelElement, element_id, self.data)

        # dict element_id is not allowed
        element_id = {"id": "path"}
        self.assertRaises(TypeError, FixedDataModelElement, element_id, self.data)

        # list element_id is not allowed
        element_id = ["path"]
        self.assertRaises(TypeError, FixedDataModelElement, element_id, self.data)

        # empty list element_id is not allowed
        element_id = []
        self.assertRaises(TypeError, FixedDataModelElement, element_id, self.data)

        # empty tuple element_id is not allowed
        element_id = ()
        self.assertRaises(TypeError, FixedDataModelElement, element_id, self.data)

        # empty set element_id is not allowed
        element_id = set()
        self.assertRaises(TypeError, FixedDataModelElement, element_id, self.data)

    def test6fixed_data_input_validation(self):
        """Check if fixed_data is validated."""
        # empty fixed_string
        fixed_string = b""
        self.assertRaises(ValueError, FixedDataModelElement, self.id_, fixed_string)

        # None fixed_string
        fixed_string = None
        self.assertRaises(TypeError, FixedDataModelElement, self.id_, fixed_string)

        # string fixed_string is not allowed
        fixed_string = "path"
        self.assertRaises(TypeError, FixedDataModelElement, self.id_, fixed_string)

        # bool fixed_string is not allowed
        fixed_string = True
        self.assertRaises(TypeError, FixedDataModelElement, self.id_, fixed_string)

        # integer fixed_string is not allowed
        fixed_string = 123
        self.assertRaises(TypeError, FixedDataModelElement, self.id_, fixed_string)

        # float fixed_string is not allowed
        fixed_string = 123.22
        self.assertRaises(TypeError, FixedDataModelElement, self.id_, fixed_string)

        # dict fixed_string is not allowed
        fixed_string = {"string": "string"}
        self.assertRaises(TypeError, FixedDataModelElement, self.id_, fixed_string)

        # list fixed_string is not allowed
        fixed_string = ["path"]
        self.assertRaises(TypeError, FixedDataModelElement, self.id_, fixed_string)

        # empty list fixed_string is not allowed
        fixed_string = []
        self.assertRaises(TypeError, FixedDataModelElement, self.id_, fixed_string)

        # empty tuple fixed_string is not allowed
        fixed_string = ()
        self.assertRaises(TypeError, FixedDataModelElement, self.id_, fixed_string)

        # empty set fixed_string is not allowed
        fixed_string = set()
        self.assertRaises(TypeError, FixedDataModelElement, self.id_, fixed_string)

    def test7get_match_element_match_context_input_validation(self):
        """Check if an exception is raised, when other classes than MatchContext are used in get_match_element."""
        model_element = FixedDataModelElement(self.id_, self.data)
        data = self.data
        model_element.get_match_element(self.path, DummyMatchContext(data))
        from aminer.parsing.MatchContext import MatchContext
        model_element.get_match_element(self.path, MatchContext(data))

        from aminer.parsing.MatchElement import MatchElement
        self.assertRaises(AttributeError, model_element.get_match_element, self.path, MatchElement(data, None, None, None))
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
