import unittest
from aminer.parsing.OptionalMatchModelElement import OptionalMatchModelElement
from unit.TestBase import TestBase, DummyMatchContext, DummyFixedDataModelElement


class OptionalMatchModelElementTest(TestBase):
    """Unittests for the OptionalMatchModelElement."""

    id_ = "optional"
    path = "path"
    fixed_id = "fixed"
    fixed_data = b"fixed data"

    def test1get_id(self):
        """Test if get_id works properly."""
        optional_match = OptionalMatchModelElement(self.id_, DummyFixedDataModelElement(self.fixed_id, self.fixed_data))
        self.assertEqual(optional_match.get_id(), self.id_)

    def test2get_child_elements(self):
        """Test if get_child_elements returns None."""
        fixed_dme = DummyFixedDataModelElement(self.fixed_id, self.fixed_data)
        optional_match = OptionalMatchModelElement(self.id_, fixed_dme)
        self.assertEqual(optional_match.get_child_elements(), [fixed_dme])

    def test3get_match_element_valid_match(self):
        """Parse matching substring from MatchContext and check if the MatchContext was updated with all characters."""
        data = b"fixed data string."
        value = self.fixed_data
        match_context = DummyMatchContext(data)
        fixed_dme = DummyFixedDataModelElement(self.fixed_id, self.fixed_data)
        optional_match = OptionalMatchModelElement(self.id_, fixed_dme)
        match_element = optional_match.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, value, value, [
            fixed_dme.get_match_element("%s/%s" % (self.path, self.id_), DummyMatchContext(data))])

    def test4get_match_element_no_match(self):
        """Parse not matching substring from MatchContext and check if the MatchContext was not changed."""
        optional_match = OptionalMatchModelElement(self.id_, DummyFixedDataModelElement(self.fixed_id, self.fixed_data))
        data = b""
        match_context = DummyMatchContext(data)
        match_element = optional_match.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, data, None, None)

        data = b"other fixed string"
        value = b""
        match_context = DummyMatchContext(data)
        match_element = optional_match.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, value, None, None)

    def test5element_id_input_validation(self):
        """Check if element_id is validated."""
        fixed_dme = DummyFixedDataModelElement(self.fixed_id, self.fixed_data)
        self.assertRaises(ValueError, OptionalMatchModelElement, "", fixed_dme)
        self.assertRaises(TypeError, OptionalMatchModelElement, None, fixed_dme)
        self.assertRaises(TypeError, OptionalMatchModelElement, b"path", fixed_dme)
        self.assertRaises(TypeError, OptionalMatchModelElement, True, fixed_dme)
        self.assertRaises(TypeError, OptionalMatchModelElement, 123, fixed_dme)
        self.assertRaises(TypeError, OptionalMatchModelElement, 123.22, fixed_dme)
        self.assertRaises(TypeError, OptionalMatchModelElement, {"id": "path"}, fixed_dme)
        self.assertRaises(TypeError, OptionalMatchModelElement, ["path"], fixed_dme)
        self.assertRaises(TypeError, OptionalMatchModelElement, [], fixed_dme)
        self.assertRaises(TypeError, OptionalMatchModelElement, (), fixed_dme)
        self.assertRaises(TypeError, OptionalMatchModelElement, set(), fixed_dme)

    def test6optional_element_input_validation(self):
        """Check if optional_element is validated."""
        self.assertRaises(TypeError, OptionalMatchModelElement, self.id_, "fixed_dme")
        self.assertRaises(TypeError, OptionalMatchModelElement, self.id_, None)
        self.assertRaises(TypeError, OptionalMatchModelElement, self.id_, b"path")
        self.assertRaises(TypeError, OptionalMatchModelElement, self.id_, True)
        self.assertRaises(TypeError, OptionalMatchModelElement, self.id_, 123)
        self.assertRaises(TypeError, OptionalMatchModelElement, self.id_, 123.22)
        self.assertRaises(TypeError, OptionalMatchModelElement, self.id_, {"id": "path"})
        self.assertRaises(TypeError, OptionalMatchModelElement, self.id_, ["path"])
        self.assertRaises(TypeError, OptionalMatchModelElement, self.id_, [])
        self.assertRaises(TypeError, OptionalMatchModelElement, self.id_, ())
        self.assertRaises(TypeError, OptionalMatchModelElement, self.id_, set())

    def test7get_match_element_match_context_input_validation(self):
        """Check if an exception is raised, when other classes than MatchContext are used in get_match_element."""
        model_element = OptionalMatchModelElement(self.id_, DummyFixedDataModelElement(self.fixed_id, self.fixed_data))
        data = b"fixed data"
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
