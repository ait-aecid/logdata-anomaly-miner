import unittest
from aminer.parsing.RepeatedElementDataModelElement import RepeatedElementDataModelElement
from aminer.parsing.MatchContext import MatchContext
from aminer.parsing.MatchElement import MatchElement
from unit.TestBase import TestBase, DummyMatchContext, DummyFixedDataModelElement


class RepeatedElementDataModelElementTest(TestBase):
    """Unittests for the RepeatedElementDataModelElement."""

    id_ = "repeated"
    path = "path"
    fixed_id = "fixed"
    fixed_data = b"fixed data "

    def test1get_id(self):
        """Test if get_id works properly."""
        repeated_dme = RepeatedElementDataModelElement(self.id_, DummyFixedDataModelElement(self.fixed_id, self.fixed_data))
        self.assertEqual(repeated_dme.get_id(), self.id_)

    def test2get_child_elements(self):
        """Test if get_child_elements returns None."""
        fixed_dme = DummyFixedDataModelElement(self.fixed_id, self.fixed_data)
        repeated_dme = RepeatedElementDataModelElement(self.id_, fixed_dme)
        self.assertEqual(repeated_dme.get_child_elements(), [fixed_dme])

    def test3get_match_element_valid_match(self):
        """Parse matching substring from MatchContext and check if the MatchContext was updated with all characters."""
        fixed_dme = DummyFixedDataModelElement(self.fixed_id, self.fixed_data)
        repeated_dme = RepeatedElementDataModelElement(self.id_, DummyFixedDataModelElement(self.fixed_id, self.fixed_data))
        data = b"fixed data string."
        value = b"fixed data "
        match_context = DummyMatchContext(data)
        match_element = repeated_dme.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, value, value, [
            fixed_dme.get_match_element("%s/%s/0" % (self.path, self.id_), DummyMatchContext(data))])

        data = b"fixed data fixed data fixed data fixed data "
        match_context = DummyMatchContext(data)
        match_element = repeated_dme.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, data, data, [
            fixed_dme.get_match_element("%s/%s/0" % (self.path, self.id_), DummyMatchContext(data)),
            fixed_dme.get_match_element("%s/%s/1" % (self.path, self.id_), DummyMatchContext(data)),
            fixed_dme.get_match_element("%s/%s/2" % (self.path, self.id_), DummyMatchContext(data)),
            fixed_dme.get_match_element("%s/%s/3" % (self.path, self.id_), DummyMatchContext(data))
        ])

        data = b"fixed data fixed data \nhere is some other string.\nfixed data fixed data "
        value = b"fixed data fixed data "
        match_context = DummyMatchContext(data)
        match_element = repeated_dme.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, value, value, [
            fixed_dme.get_match_element("%s/%s/0" % (self.path, self.id_), DummyMatchContext(data)),
            fixed_dme.get_match_element("%s/%s/1" % (self.path, self.id_), DummyMatchContext(data))
        ])

    def test4get_match_element_min_max_repeats(self):
        """This test case verifies the functionality of setting the minimal and maximal repeats."""
        fixed_dme = DummyFixedDataModelElement(self.fixed_id, self.fixed_data)
        repeated_dme = RepeatedElementDataModelElement(self.id_, fixed_dme, min_repeat=2, max_repeat=5)
        same_min_max_repeat_dme = RepeatedElementDataModelElement(self.id_, fixed_dme, min_repeat=3, max_repeat=3)
        data = b"other data"
        match_context = DummyMatchContext(data)
        match_element = repeated_dme.get_match_element(self.path, match_context)
        self.compare_no_match_results(data, match_element, match_context)
        match_context = DummyMatchContext(data)
        match_element = same_min_max_repeat_dme.get_match_element(self.path, match_context)
        self.compare_no_match_results(data, match_element, match_context)

        data = b"fixed data "
        match_context = DummyMatchContext(data)
        match_element = repeated_dme.get_match_element(self.path, match_context)
        self.compare_no_match_results(data, match_element, match_context)

        match_context = DummyMatchContext(data)
        match_element = same_min_max_repeat_dme.get_match_element(self.path, match_context)
        self.compare_no_match_results(data, match_element, match_context)

        data = b"fixed data fixed data "
        match_context = DummyMatchContext(data)
        match_element = repeated_dme.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, data, data, [
            fixed_dme.get_match_element("%s/%s/0" % (self.path, self.id_), DummyMatchContext(data)),
            fixed_dme.get_match_element("%s/%s/1" % (self.path, self.id_), DummyMatchContext(data))])

        match_context = DummyMatchContext(data)
        match_element = same_min_max_repeat_dme.get_match_element(self.path, match_context)
        self.compare_no_match_results(data, match_element, match_context)

        data = b"fixed data fixed data fixed data "
        match_context = DummyMatchContext(data)
        match_element = repeated_dme.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, data, data, [
            fixed_dme.get_match_element("%s/%s/0" % (self.path, self.id_), DummyMatchContext(data)),
            fixed_dme.get_match_element("%s/%s/1" % (self.path, self.id_), DummyMatchContext(data)),
            fixed_dme.get_match_element("%s/%s/2" % (self.path, self.id_), DummyMatchContext(data))])

        match_context = DummyMatchContext(data)
        match_element = same_min_max_repeat_dme.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, data, data, [
            fixed_dme.get_match_element("%s/%s/0" % (self.path, self.id_), DummyMatchContext(data)),
            fixed_dme.get_match_element("%s/%s/1" % (self.path, self.id_), DummyMatchContext(data)),
            fixed_dme.get_match_element("%s/%s/2" % (self.path, self.id_), DummyMatchContext(data))])

        data = b"fixed data fixed data fixed data fixed data "
        match_context = DummyMatchContext(data)
        match_element = repeated_dme.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, data, data, [
            fixed_dme.get_match_element("%s/%s/0" % (self.path, self.id_), DummyMatchContext(data)),
            fixed_dme.get_match_element("%s/%s/1" % (self.path, self.id_), DummyMatchContext(data)),
            fixed_dme.get_match_element("%s/%s/2" % (self.path, self.id_), DummyMatchContext(data)),
            fixed_dme.get_match_element("%s/%s/3" % (self.path, self.id_), DummyMatchContext(data))])

        match_context = DummyMatchContext(data)
        match_element = same_min_max_repeat_dme.get_match_element(self.path, match_context)
        self.compare_no_match_results(data, match_element, match_context)

        data = b"fixed data fixed data fixed data fixed data fixed data "
        match_context = DummyMatchContext(data)
        match_element = repeated_dme.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, data, data, [
            fixed_dme.get_match_element("%s/%s/0" % (self.path, self.id_), DummyMatchContext(data)),
            fixed_dme.get_match_element("%s/%s/1" % (self.path, self.id_), DummyMatchContext(data)),
            fixed_dme.get_match_element("%s/%s/2" % (self.path, self.id_), DummyMatchContext(data)),
            fixed_dme.get_match_element("%s/%s/3" % (self.path, self.id_), DummyMatchContext(data)),
            fixed_dme.get_match_element("%s/%s/4" % (self.path, self.id_), DummyMatchContext(data))])

        match_context = DummyMatchContext(data)
        match_element = same_min_max_repeat_dme.get_match_element(self.path, match_context)
        self.compare_no_match_results(data, match_element, match_context)

        data = b"fixed data fixed data fixed data fixed data fixed data fixed data "
        match_context = DummyMatchContext(data)
        match_element = repeated_dme.get_match_element(self.path, match_context)
        self.compare_no_match_results(data, match_element, match_context)

        match_context = DummyMatchContext(data)
        match_element = same_min_max_repeat_dme.get_match_element(self.path, match_context)
        self.compare_no_match_results(data, match_element, match_context)

    def test5element_id_input_validation(self):
        """Check if element_id is validated."""
        fixed_dme = DummyFixedDataModelElement(self.fixed_id, self.fixed_data)
        self.assertRaises(ValueError, RepeatedElementDataModelElement, "", fixed_dme)
        self.assertRaises(TypeError, RepeatedElementDataModelElement, None, fixed_dme)
        self.assertRaises(TypeError, RepeatedElementDataModelElement, b"path", fixed_dme)
        self.assertRaises(TypeError, RepeatedElementDataModelElement, True, fixed_dme)
        self.assertRaises(TypeError, RepeatedElementDataModelElement, 123, fixed_dme)
        self.assertRaises(TypeError, RepeatedElementDataModelElement, 123.22, fixed_dme)
        self.assertRaises(TypeError, RepeatedElementDataModelElement, {"id": "path"}, fixed_dme)
        self.assertRaises(TypeError, RepeatedElementDataModelElement, ["path"], fixed_dme)
        self.assertRaises(TypeError, RepeatedElementDataModelElement, [], fixed_dme)
        self.assertRaises(TypeError, RepeatedElementDataModelElement, (), fixed_dme)
        self.assertRaises(TypeError, RepeatedElementDataModelElement, set(), fixed_dme)

    def test6repeated_element_input_validation(self):
        """Check if repeated_element is validated."""
        self.assertRaises(TypeError, RepeatedElementDataModelElement, self.id_, "string")
        self.assertRaises(TypeError, RepeatedElementDataModelElement, self.id_, None)
        self.assertRaises(TypeError, RepeatedElementDataModelElement, self.id_, b"path")
        self.assertRaises(TypeError, RepeatedElementDataModelElement, self.id_, True)
        self.assertRaises(TypeError, RepeatedElementDataModelElement, self.id_, 123)
        self.assertRaises(TypeError, RepeatedElementDataModelElement, self.id_, 123.22)
        self.assertRaises(TypeError, RepeatedElementDataModelElement, self.id_, {"id": "path"})
        self.assertRaises(TypeError, RepeatedElementDataModelElement, self.id_, ["path"])
        self.assertRaises(TypeError, RepeatedElementDataModelElement, self.id_, [])
        self.assertRaises(TypeError, RepeatedElementDataModelElement, self.id_, ())
        self.assertRaises(TypeError, RepeatedElementDataModelElement, self.id_, set())

    def test7min_repeat_input_validation(self):
        """Check if min_repeat is validated."""
        fixed_dme = DummyFixedDataModelElement(self.fixed_id, self.fixed_data)
        self.assertRaises(TypeError, RepeatedElementDataModelElement, self.id_, fixed_dme, min_repeat="string")
        self.assertRaises(TypeError, RepeatedElementDataModelElement, self.id_, fixed_dme, min_repeat=None)
        self.assertRaises(TypeError, RepeatedElementDataModelElement, self.id_, fixed_dme, min_repeat=b"path")
        self.assertRaises(TypeError, RepeatedElementDataModelElement, self.id_, fixed_dme, min_repeat=True)
        self.assertRaises(ValueError, RepeatedElementDataModelElement, self.id_, fixed_dme, min_repeat=-1)
        self.assertRaises(TypeError, RepeatedElementDataModelElement, self.id_, fixed_dme, min_repeat=123.22)
        self.assertRaises(TypeError, RepeatedElementDataModelElement, self.id_, fixed_dme, min_repeat={"id": "path"})
        self.assertRaises(TypeError, RepeatedElementDataModelElement, self.id_, fixed_dme, min_repeat=["path"])
        self.assertRaises(TypeError, RepeatedElementDataModelElement, self.id_, fixed_dme, min_repeat=[])
        self.assertRaises(TypeError, RepeatedElementDataModelElement, self.id_, fixed_dme, min_repeat=())
        self.assertRaises(TypeError, RepeatedElementDataModelElement, self.id_, fixed_dme, min_repeat=set())

    def test8max_repeat_input_validation(self):
        """Check if max_repeat is validated."""
        fixed_dme = DummyFixedDataModelElement(self.fixed_id, self.fixed_data)
        self.assertRaises(TypeError, RepeatedElementDataModelElement, self.id_, fixed_dme, max_repeat="string")
        self.assertRaises(TypeError, RepeatedElementDataModelElement, self.id_, fixed_dme, max_repeat=None)
        self.assertRaises(TypeError, RepeatedElementDataModelElement, self.id_, fixed_dme, max_repeat=b"path")
        self.assertRaises(TypeError, RepeatedElementDataModelElement, self.id_, fixed_dme, max_repeat=True)
        self.assertRaises(ValueError, RepeatedElementDataModelElement, self.id_, fixed_dme, max_repeat=0)
        self.assertRaises(ValueError, RepeatedElementDataModelElement, self.id_, fixed_dme, max_repeat=10, min_repeat=11)
        self.assertRaises(TypeError, RepeatedElementDataModelElement, self.id_, fixed_dme, max_repeat=123.22)
        self.assertRaises(TypeError, RepeatedElementDataModelElement, self.id_, fixed_dme, max_repeat={"id": "path"})
        self.assertRaises(TypeError, RepeatedElementDataModelElement, self.id_, fixed_dme, max_repeat=["path"])
        self.assertRaises(TypeError, RepeatedElementDataModelElement, self.id_, fixed_dme, max_repeat=[])
        self.assertRaises(TypeError, RepeatedElementDataModelElement, self.id_, fixed_dme, max_repeat=())
        self.assertRaises(TypeError, RepeatedElementDataModelElement, self.id_, fixed_dme, max_repeat=set())

    def test9get_match_element_match_context_input_validation(self):
        """Check if an exception is raised, when other classes than MatchContext are used in get_match_element."""
        model_element = RepeatedElementDataModelElement(self.id_, DummyFixedDataModelElement(self.fixed_id, self.fixed_data))
        data = b"fixed data"
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
