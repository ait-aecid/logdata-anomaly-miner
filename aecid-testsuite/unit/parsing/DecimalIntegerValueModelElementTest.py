import unittest
from aminer.parsing.DecimalIntegerValueModelElement import DecimalIntegerValueModelElement
from aminer.parsing.MatchContext import MatchContext
from aminer.parsing.MatchElement import MatchElement
from unit.TestBase import TestBase, DummyMatchContext


class DecimalIntegerValueModelElementTest(TestBase):
    """Unittests for the DecimalIntegerValueModelElement."""

    id_ = "integer"
    path = "path"

    def test1get_match_element_default_values(self):
        """Test valid integer values with default values of value_sign_type and value_pad_type."""
        decimal_integer_value_me = DecimalIntegerValueModelElement(
            self.id_, DecimalIntegerValueModelElement.SIGN_TYPE_NONE, DecimalIntegerValueModelElement.PAD_TYPE_NONE)
        data = b"22.25 some string."
        value = b"22"
        match_context = DummyMatchContext(data)
        match_element = decimal_integer_value_me.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, value, 22, None)

        data = b"0.25 some string."
        value = b"0"
        match_context = DummyMatchContext(data)
        match_element = decimal_integer_value_me.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, value, 0, None)

        data = b"22 some string."
        value = b"22"
        match_context = DummyMatchContext(data)
        match_element = decimal_integer_value_me.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, value, 22, None)

        data = b"22.12.2021 some string."
        value = b"22"
        match_context = DummyMatchContext(data)
        match_element = decimal_integer_value_me.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, value, 22, None)

        data = b"22. some string"
        value = b"22"
        match_context = DummyMatchContext(data)
        match_element = decimal_integer_value_me.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, value, 22, None)

        data = b"0 some string"
        value = b"0"
        match_context = DummyMatchContext(data)
        match_element = decimal_integer_value_me.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, value, 0, None)

    def test2get_match_element_default_values_no_match(self):
        """Test not matching values with default values of value_sign_type and value_pad_type."""
        decimal_integer_value_me = DecimalIntegerValueModelElement(
            self.id_, DecimalIntegerValueModelElement.SIGN_TYPE_NONE, DecimalIntegerValueModelElement.PAD_TYPE_NONE)
        data = b"+22.25"
        match_context = DummyMatchContext(data)
        match_element = decimal_integer_value_me.get_match_element(self.path, match_context)
        self.compare_no_match_results(data, match_element, match_context)

        data = b"-22.25"
        match_context = DummyMatchContext(data)
        match_element = decimal_integer_value_me.get_match_element(self.path, match_context)
        self.compare_no_match_results(data, match_element, match_context)

        data = b"22,25"
        value = b"22"
        match_context = DummyMatchContext(data)
        match_element = decimal_integer_value_me.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, value, 22, None)

        data = b".25"
        match_context = DummyMatchContext(data)
        match_element = decimal_integer_value_me.get_match_element(self.path, match_context)
        self.compare_no_match_results(data, match_element, match_context)

        data = b"025"
        match_context = DummyMatchContext(data)
        match_element = decimal_integer_value_me.get_match_element(self.path, match_context)
        self.compare_no_match_results(data, match_element, match_context)

        data = b"0025"
        match_context = DummyMatchContext(data)
        match_element = decimal_integer_value_me.get_match_element(self.path, match_context)
        self.compare_no_match_results(data, match_element, match_context)

        data = b" 25"
        match_context = DummyMatchContext(data)
        match_element = decimal_integer_value_me.get_match_element(self.path, match_context)
        self.compare_no_match_results(data, match_element, match_context)

        data = b"  25"
        match_context = DummyMatchContext(data)
        match_element = decimal_integer_value_me.get_match_element(self.path, match_context)
        self.compare_no_match_results(data, match_element, match_context)

        data = b"1e-5"
        value = b"1"
        match_context = DummyMatchContext(data)
        match_element = decimal_integer_value_me.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, value, 1, None)

        data = b"e+10"
        match_context = DummyMatchContext(data)
        match_element = decimal_integer_value_me.get_match_element(self.path, match_context)
        self.compare_no_match_results(data, match_element, match_context)

        data = b"1e+0"
        value = b"1"
        match_context = DummyMatchContext(data)
        match_element = decimal_integer_value_me.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, value, 1, None)

        data = b"00"
        match_context = DummyMatchContext(data)
        match_element = decimal_integer_value_me.get_match_element(self.path, match_context)
        self.compare_no_match_results(data, match_element, match_context)

        data = b"no number 22 some string."
        match_context = DummyMatchContext(data)
        match_element = decimal_integer_value_me.get_match_element(self.path, match_context)
        self.compare_no_match_results(data, match_element, match_context)

    def test3get_match_element_optional_zero_values(self):
        """Test valid float values with "optional" or "zero" values of value_sign_type and value_pad_type."""
        decimal_integer_value_me = DecimalIntegerValueModelElement(
            self.id_, DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL, DecimalIntegerValueModelElement.PAD_TYPE_ZERO)
        data = b"22.25 some string."
        value = b"22"
        match_context = DummyMatchContext(data)
        match_element = decimal_integer_value_me.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, value, 22, None)

        data = b"-22.25 some string."
        value = b"-22"
        match_context = DummyMatchContext(data)
        match_element = decimal_integer_value_me.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, value, -22, None)

        data = b"0.25 some string."
        value = b"0"
        match_context = DummyMatchContext(data)
        match_element = decimal_integer_value_me.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, value, 0, None)

        data = b"22 some string."
        value = b"22"
        match_context = DummyMatchContext(data)
        match_element = decimal_integer_value_me.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, value, 22, None)

        data = b"22.12.2021 some string."
        value = b"22"
        match_context = DummyMatchContext(data)
        match_element = decimal_integer_value_me.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, value, 22, None)

        data = b"22. some string"
        value = b"22"
        match_context = DummyMatchContext(data)
        match_element = decimal_integer_value_me.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, value, 22, None)

        data = b"025 some string"
        value = b"025"
        match_context = DummyMatchContext(data)
        match_element = decimal_integer_value_me.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, value, 25, None)

        data = b"0025 some string"
        value = b"0025"
        match_context = DummyMatchContext(data)
        match_element = decimal_integer_value_me.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, value, 25, None)

        data = b"0025.22 some string"
        value = b"0025"
        match_context = DummyMatchContext(data)
        match_element = decimal_integer_value_me.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, value, 25, None)

        data = b"1e-5 some string"
        value = b"1"
        match_context = DummyMatchContext(data)
        match_element = decimal_integer_value_me.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, value, 1, None)

        data = b"1e+0 some string"
        value = b"1"
        match_context = DummyMatchContext(data)
        match_element = decimal_integer_value_me.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, value, 1, None)

        data = b"0 some string"
        value = b"0"
        match_context = DummyMatchContext(data)
        match_element = decimal_integer_value_me.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, value, 0, None)

        data = b"00 some string"
        value = b"00"
        match_context = DummyMatchContext(data)
        match_element = decimal_integer_value_me.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, value, 0, None)

    def test4get_match_element_optional_zero_values_no_match(self):
        """Test not matching values with default values of value_sign_type and value_pad_type."""
        decimal_integer_value_me = DecimalIntegerValueModelElement(
            self.id_, DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL, DecimalIntegerValueModelElement.PAD_TYPE_ZERO)
        data = b"+22.25"
        match_context = DummyMatchContext(data)
        match_element = decimal_integer_value_me.get_match_element(self.path, match_context)
        self.compare_no_match_results(data, match_element, match_context)

        data = b"22,25"
        value = b"22"
        match_context = DummyMatchContext(data)
        match_element = decimal_integer_value_me.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, value, 22, None)

        data = b".25"
        match_context = DummyMatchContext(data)
        match_element = decimal_integer_value_me.get_match_element(self.path, match_context)
        self.compare_no_match_results(data, match_element, match_context)

        data = b" 25"
        match_context = DummyMatchContext(data)
        match_element = decimal_integer_value_me.get_match_element(self.path, match_context)
        self.compare_no_match_results(data, match_element, match_context)

        data = b"  25"
        match_context = DummyMatchContext(data)
        match_element = decimal_integer_value_me.get_match_element(self.path, match_context)
        self.compare_no_match_results(data, match_element, match_context)

        data = b"e+10"
        match_context = DummyMatchContext(data)
        match_element = decimal_integer_value_me.get_match_element(self.path, match_context)
        self.compare_no_match_results(data, match_element, match_context)

        data = b"no number 22 some string."
        match_context = DummyMatchContext(data)
        match_element = decimal_integer_value_me.get_match_element(self.path, match_context)
        self.compare_no_match_results(data, match_element, match_context)

    def test5get_match_element_mandatory_blank_values(self):
        """Test valid float values with "mandatory" or "blank" values of value_sign_type and value_pad_type."""
        decimal_integer_value_me = DecimalIntegerValueModelElement(
            self.id_, DecimalIntegerValueModelElement.SIGN_TYPE_MANDATORY, DecimalIntegerValueModelElement.PAD_TYPE_BLANK)
        data = b"+22.25 some string."
        value = b"+22"
        match_context = DummyMatchContext(data)
        match_element = decimal_integer_value_me.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, value, 22, None)

        data = b"-22.25 some string."
        value = b"-22"
        match_context = DummyMatchContext(data)
        match_element = decimal_integer_value_me.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, value, -22, None)

        data = b"+0.25 some string."
        value = b"+0"
        match_context = DummyMatchContext(data)
        match_element = decimal_integer_value_me.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, value, 0, None)

        data = b"+22 some string."
        value = b"+22"
        match_context = DummyMatchContext(data)
        match_element = decimal_integer_value_me.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, value, 22, None)

        data = b"+22. some string"
        value = b"+22"
        match_context = DummyMatchContext(data)
        match_element = decimal_integer_value_me.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, value, 22, None)

        data = b"+ 25 some string"
        value = b"+ 25"
        match_context = DummyMatchContext(data)
        match_element = decimal_integer_value_me.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, value, 25, None)

        data = b"- 25 some string"
        value = b"- 25"
        match_context = DummyMatchContext(data)
        match_element = decimal_integer_value_me.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, value, -25, None)

        data = b"+1e-5 some string"
        value = b"+1"
        match_context = DummyMatchContext(data)
        match_element = decimal_integer_value_me.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, value, 1, None)

        data = b"+1e+0 some string"
        value = b"+1"
        match_context = DummyMatchContext(data)
        match_element = decimal_integer_value_me.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, value, 1, None)

        data = b"+ 1e+0 some string"
        value = b"+ 1"
        match_context = DummyMatchContext(data)
        match_element = decimal_integer_value_me.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, value, 1, None)

        data = b"+0 some string"
        value = b"+0"
        match_context = DummyMatchContext(data)
        match_element = decimal_integer_value_me.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, value, 0, None)

    def test6get_match_element_mandatory_blank_values_no_match(self):
        """Test not matching values with default values of value_sign_type and value_pad_type."""
        decimal_integer_value_me = DecimalIntegerValueModelElement(
            self.id_, DecimalIntegerValueModelElement.SIGN_TYPE_MANDATORY, DecimalIntegerValueModelElement.PAD_TYPE_BLANK)
        data = b"22.25"
        match_context = DummyMatchContext(data)
        match_element = decimal_integer_value_me.get_match_element(self.path, match_context)
        self.compare_no_match_results(data, match_element, match_context)

        data = b"+  22.25"
        match_context = DummyMatchContext(data)
        match_element = decimal_integer_value_me.get_match_element(self.path, match_context)
        self.compare_no_match_results(data, match_element, match_context)

        data = b"-  22.25"
        match_context = DummyMatchContext(data)
        match_element = decimal_integer_value_me.get_match_element(self.path, match_context)
        self.compare_no_match_results(data, match_element, match_context)

        data = b"+22,25"
        value = b"+22"
        match_context = DummyMatchContext(data)
        match_element = decimal_integer_value_me.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, value, 22, None)

        data = b"22,25"
        match_context = DummyMatchContext(data)
        match_element = decimal_integer_value_me.get_match_element(self.path, match_context)
        self.compare_no_match_results(data, match_element, match_context)

        data = b"22.12.2021 some string."
        match_context = DummyMatchContext(data)
        match_element = decimal_integer_value_me.get_match_element(self.path, match_context)
        self.compare_no_match_results(data, match_element, match_context)

        data = b".25"
        match_context = DummyMatchContext(data)
        match_element = decimal_integer_value_me.get_match_element(self.path, match_context)
        self.compare_no_match_results(data, match_element, match_context)

        data = b" +25"
        match_context = DummyMatchContext(data)
        match_element = decimal_integer_value_me.get_match_element(self.path, match_context)
        self.compare_no_match_results(data, match_element, match_context)

        data = b" -25"
        match_context = DummyMatchContext(data)
        match_element = decimal_integer_value_me.get_match_element(self.path, match_context)
        self.compare_no_match_results(data, match_element, match_context)

        data = b"025"
        match_context = DummyMatchContext(data)
        match_element = decimal_integer_value_me.get_match_element(self.path, match_context)
        self.compare_no_match_results(data, match_element, match_context)

        data = b"0025"
        match_context = DummyMatchContext(data)
        match_element = decimal_integer_value_me.get_match_element(self.path, match_context)
        self.compare_no_match_results(data, match_element, match_context)

        data = b"e+10"
        match_context = DummyMatchContext(data)
        match_element = decimal_integer_value_me.get_match_element(self.path, match_context)
        self.compare_no_match_results(data, match_element, match_context)

        data = b"00"
        match_context = DummyMatchContext(data)
        match_element = decimal_integer_value_me.get_match_element(self.path, match_context)
        self.compare_no_match_results(data, match_element, match_context)

        data = b"no number 22 some string."
        match_context = DummyMatchContext(data)
        match_element = decimal_integer_value_me.get_match_element(self.path, match_context)
        self.compare_no_match_results(data, match_element, match_context)

    def test7element_id_input_validation(self):
        """Check if element_id is validated."""
        self.assertRaises(ValueError, DecimalIntegerValueModelElement, "")  # empty element_id
        self.assertRaises(TypeError, DecimalIntegerValueModelElement, None)  # None element_id
        self.assertRaises(TypeError, DecimalIntegerValueModelElement, b"path")  # bytes element_id is not allowed
        self.assertRaises(TypeError, DecimalIntegerValueModelElement, True)  # boolean element_id is not allowed
        self.assertRaises(TypeError, DecimalIntegerValueModelElement, 123)  # integer element_id is not allowed
        self.assertRaises(TypeError, DecimalIntegerValueModelElement, 123.22)  # float element_id is not allowed
        self.assertRaises(TypeError, DecimalIntegerValueModelElement, {"id": "path"})  # dict element_id is not allowed
        self.assertRaises(TypeError, DecimalIntegerValueModelElement, ["path"])  # list element_id is not allowed
        self.assertRaises(TypeError, DecimalIntegerValueModelElement, [])  # empty list element_id is not allowed
        self.assertRaises(TypeError, DecimalIntegerValueModelElement, ())  # empty tuple element_id is not allowed
        self.assertRaises(TypeError, DecimalIntegerValueModelElement, set())  # empty set element_id is not allowed

    def test9value_sign_type_input_validation(self):
        """Check if value_sign_type is validated."""
        DecimalIntegerValueModelElement(self.id_, value_sign_type="none")
        DecimalIntegerValueModelElement(self.id_, value_sign_type="optional")
        DecimalIntegerValueModelElement(self.id_, value_sign_type="mandatory")

        self.assertRaises(ValueError, DecimalIntegerValueModelElement, self.id_, value_sign_type="None")
        self.assertRaises(TypeError, DecimalIntegerValueModelElement, self.id_, value_sign_type=None)
        self.assertRaises(TypeError, DecimalIntegerValueModelElement, self.id_, value_sign_type=b"none")
        self.assertRaises(TypeError, DecimalIntegerValueModelElement, self.id_, value_sign_type=True)
        self.assertRaises(TypeError, DecimalIntegerValueModelElement, self.id_, value_sign_type=123)
        self.assertRaises(TypeError, DecimalIntegerValueModelElement, self.id_, value_sign_type=123.22)
        self.assertRaises(TypeError, DecimalIntegerValueModelElement, self.id_, value_sign_type={"value_sign_type": "none"})
        self.assertRaises(TypeError, DecimalIntegerValueModelElement, self.id_, value_sign_type=["none"])
        self.assertRaises(TypeError, DecimalIntegerValueModelElement, self.id_, value_sign_type=[])
        self.assertRaises(TypeError, DecimalIntegerValueModelElement, self.id_, value_sign_type=())
        self.assertRaises(TypeError, DecimalIntegerValueModelElement, self.id_, value_sign_type=set())

    def test10value_pad_type_input_validation(self):
        """Check if value_pad_type is validated."""
        DecimalIntegerValueModelElement(self.id_, value_pad_type="none")
        DecimalIntegerValueModelElement(self.id_, value_pad_type="zero")
        DecimalIntegerValueModelElement(self.id_, value_pad_type="blank")

        self.assertRaises(ValueError, DecimalIntegerValueModelElement, self.id_, value_pad_type="None")
        self.assertRaises(TypeError, DecimalIntegerValueModelElement, self.id_, value_pad_type=None)
        self.assertRaises(TypeError, DecimalIntegerValueModelElement, self.id_, value_pad_type=b"none")
        self.assertRaises(TypeError, DecimalIntegerValueModelElement, self.id_, value_pad_type=True)
        self.assertRaises(TypeError, DecimalIntegerValueModelElement, self.id_, value_pad_type=123)
        self.assertRaises(TypeError, DecimalIntegerValueModelElement, self.id_, value_pad_type=123.22)
        self.assertRaises(TypeError, DecimalIntegerValueModelElement, self.id_, value_pad_type={"value_sign_type": "none"})
        self.assertRaises(TypeError, DecimalIntegerValueModelElement, self.id_, value_pad_type=["none"])
        self.assertRaises(TypeError, DecimalIntegerValueModelElement, self.id_, value_pad_type=[])
        self.assertRaises(TypeError, DecimalIntegerValueModelElement, self.id_, value_pad_type=())
        self.assertRaises(TypeError, DecimalIntegerValueModelElement, self.id_, value_pad_type=set())

    def test11get_match_element_match_context_input_validation(self):
        """Check if an exception is raised, when other classes than MatchContext are used in get_match_element."""
        model_element = DecimalIntegerValueModelElement(self.id_)
        data = b"123.22"
        model_element.get_match_element(self.path, DummyMatchContext(data))
        model_element.get_match_element(self.path, MatchContext(data))

        self.assertRaises(AttributeError, model_element.get_match_element, self.path, MatchElement(None, data, None, None))
        self.assertRaises(AttributeError, model_element.get_match_element, self.path, data)
        self.assertRaises(AttributeError, model_element.get_match_element, self.path, data.decode())
        self.assertRaises(AttributeError, model_element.get_match_element, self.path, True)
        self.assertRaises(AttributeError, model_element.get_match_element, self.path, 123)
        self.assertRaises(AttributeError, model_element.get_match_element, self.path, 123.22)
        self.assertRaises(AttributeError, model_element.get_match_element, self.path, None)
        self.assertRaises(AttributeError, model_element.get_match_element, self.path, [])
        self.assertRaises(AttributeError, model_element.get_match_element, self.path, {"key": MatchContext(data)})
        self.assertRaises(AttributeError, model_element.get_match_element, self.path, set())
        self.assertRaises(AttributeError, model_element.get_match_element, self.path, ())
        self.assertRaises(AttributeError, model_element.get_match_element, self.path, model_element)


if __name__ == "__main__":
    unittest.main()
