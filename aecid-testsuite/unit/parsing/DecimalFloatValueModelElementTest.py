import unittest
from aminer.parsing.DecimalFloatValueModelElement import DecimalFloatValueModelElement
from aminer.parsing.MatchContext import MatchContext
from aminer.parsing.MatchElement import MatchElement
from unit.TestBase import TestBase, DummyMatchContext


class DecimalFloatValueModelElementTest(TestBase):
    """Unittests for the DecimalFloatValueModelElement."""

    id_ = "float"
    path = "path"

    def test1get_match_element_default_values(self):
        """Test valid float values with default values of value_sign_type, value_pad_type and exponent_type."""
        decimal_float_value_me = DecimalFloatValueModelElement(
            self.id_, DecimalFloatValueModelElement.SIGN_TYPE_NONE, DecimalFloatValueModelElement.PAD_TYPE_NONE,
            DecimalFloatValueModelElement.EXP_TYPE_NONE)
        data = b"22.25 some string."
        value = b"22.25"
        match_context = DummyMatchContext(data)
        match_element = decimal_float_value_me.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, value, 22.25, None)

        data = b"0.25 some string."
        value = b"0.25"
        match_context = DummyMatchContext(data)
        match_element = decimal_float_value_me.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, value, 0.25, None)

        data = b"22 some string."
        value = b"22"
        match_context = DummyMatchContext(data)
        match_element = decimal_float_value_me.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, value, 22, None)

        data = b"22.12.2021 some string."
        value = b"22.12"
        match_context = DummyMatchContext(data)
        match_element = decimal_float_value_me.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, value, 22.12, None)

        data = b"22. some string"
        value = b"22."
        match_context = DummyMatchContext(data)
        match_element = decimal_float_value_me.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, value, 22.0, None)

        data = b"0 some string"
        value = b"0"
        match_context = DummyMatchContext(data)
        match_element = decimal_float_value_me.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, value, 0, None)

    def test2get_match_element_default_values_no_match(self):
        """Test not matching values with default values of value_sign_type, value_pad_type and exponent_type."""
        decimal_float_value_me = DecimalFloatValueModelElement(
            self.id_, DecimalFloatValueModelElement.SIGN_TYPE_NONE, DecimalFloatValueModelElement.PAD_TYPE_NONE,
            DecimalFloatValueModelElement.EXP_TYPE_NONE)
        data = b"+22.25"
        match_context = DummyMatchContext(data)
        match_element = decimal_float_value_me.get_match_element(self.path, match_context)
        self.compare_no_match_results(data, match_element, match_context)

        data = b"-22.25"
        match_context = DummyMatchContext(data)
        match_element = decimal_float_value_me.get_match_element(self.path, match_context)
        self.compare_no_match_results(data, match_element, match_context)

        data = b"22,25"
        value = b"22"
        match_context = DummyMatchContext(data)
        match_element = decimal_float_value_me.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, value, 22, None)

        data = b".25"
        match_context = DummyMatchContext(data)
        match_element = decimal_float_value_me.get_match_element(self.path, match_context)
        self.compare_no_match_results(data, match_element, match_context)

        data = b"025"
        match_context = DummyMatchContext(data)
        match_element = decimal_float_value_me.get_match_element(self.path, match_context)
        self.compare_no_match_results(data, match_element, match_context)

        data = b"0025"
        match_context = DummyMatchContext(data)
        match_element = decimal_float_value_me.get_match_element(self.path, match_context)
        self.compare_no_match_results(data, match_element, match_context)

        data = b" 25"
        match_context = DummyMatchContext(data)
        match_element = decimal_float_value_me.get_match_element(self.path, match_context)
        self.compare_no_match_results(data, match_element, match_context)

        data = b"  25"
        match_context = DummyMatchContext(data)
        match_element = decimal_float_value_me.get_match_element(self.path, match_context)
        self.compare_no_match_results(data, match_element, match_context)

        data = b"1e-5"
        value = b"1"
        match_context = DummyMatchContext(data)
        match_element = decimal_float_value_me.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, value, 1, None)

        data = b"e+10"
        match_context = DummyMatchContext(data)
        match_element = decimal_float_value_me.get_match_element(self.path, match_context)
        self.compare_no_match_results(data, match_element, match_context)

        data = b"1e+0"
        value = b"1"
        match_context = DummyMatchContext(data)
        match_element = decimal_float_value_me.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, value, 1, None)

        data = b"00"
        match_context = DummyMatchContext(data)
        match_element = decimal_float_value_me.get_match_element(self.path, match_context)
        self.compare_no_match_results(data, match_element, match_context)

    def test3get_match_element_optional_zero_values(self):
        """Test valid float values with "optional" or "zero" values of value_sign_type, value_pad_type and exponent_type."""
        decimal_float_value_me = DecimalFloatValueModelElement(
            self.id_, DecimalFloatValueModelElement.SIGN_TYPE_OPTIONAL, DecimalFloatValueModelElement.PAD_TYPE_ZERO,
            DecimalFloatValueModelElement.EXP_TYPE_OPTIONAL)
        data = b"22.25 some string."
        value = b"22.25"
        match_context = DummyMatchContext(data)
        match_element = decimal_float_value_me.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, value, 22.25, None)

        data = b"-22.25 some string."
        value = b"-22.25"
        match_context = DummyMatchContext(data)
        match_element = decimal_float_value_me.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, value, -22.25, None)

        data = b"0.25 some string."
        value = b"0.25"
        match_context = DummyMatchContext(data)
        match_element = decimal_float_value_me.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, value, 0.25, None)

        data = b"22 some string."
        value = b"22"
        match_context = DummyMatchContext(data)
        match_element = decimal_float_value_me.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, value, 22, None)

        data = b"22.12.2021 some string."
        value = b"22.12"
        match_context = DummyMatchContext(data)
        match_element = decimal_float_value_me.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, value, 22.12, None)

        data = b"22. some string"
        value = b"22."
        match_context = DummyMatchContext(data)
        match_element = decimal_float_value_me.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, value, 22.0, None)

        data = b"025 some string"
        value = b"025"
        match_context = DummyMatchContext(data)
        match_element = decimal_float_value_me.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, value, 25, None)

        data = b"0025 some string"
        value = b"0025"
        match_context = DummyMatchContext(data)
        match_element = decimal_float_value_me.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, value, 25, None)

        data = b"0025.22 some string"
        value = b"0025.22"
        match_context = DummyMatchContext(data)
        match_element = decimal_float_value_me.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, value, 25.22, None)

        data = b"1e-5 some string"
        value = b"1e-5"
        match_context = DummyMatchContext(data)
        match_element = decimal_float_value_me.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, value, 1e-5, None)

        data = b"1e+0 some string"
        value = b"1e+0"
        match_context = DummyMatchContext(data)
        match_element = decimal_float_value_me.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, value, 1, None)

        data = b"0 some string"
        value = b"0"
        match_context = DummyMatchContext(data)
        match_element = decimal_float_value_me.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, value, 0, None)

        data = b"00 some string"
        value = b"00"
        match_context = DummyMatchContext(data)
        match_element = decimal_float_value_me.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, value, 0, None)

    def test4get_match_element_optional_zero_values_no_match(self):
        """Test not matching values with default values of value_sign_type, value_pad_type and exponent_type."""
        decimal_float_value_me = DecimalFloatValueModelElement(
            self.id_, DecimalFloatValueModelElement.SIGN_TYPE_OPTIONAL, DecimalFloatValueModelElement.PAD_TYPE_ZERO,
            DecimalFloatValueModelElement.EXP_TYPE_OPTIONAL)
        data = b"+22.25"
        match_context = DummyMatchContext(data)
        match_element = decimal_float_value_me.get_match_element(self.path, match_context)
        self.compare_no_match_results(data, match_element, match_context)

        data = b"22,25"
        value = b"22"
        match_context = DummyMatchContext(data)
        match_element = decimal_float_value_me.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, value, 22, None)

        data = b".25"
        match_context = DummyMatchContext(data)
        match_element = decimal_float_value_me.get_match_element(self.path, match_context)
        self.compare_no_match_results(data, match_element, match_context)

        data = b" 25"
        match_context = DummyMatchContext(data)
        match_element = decimal_float_value_me.get_match_element(self.path, match_context)
        self.compare_no_match_results(data, match_element, match_context)

        data = b"  25"
        match_context = DummyMatchContext(data)
        match_element = decimal_float_value_me.get_match_element(self.path, match_context)
        self.compare_no_match_results(data, match_element, match_context)

        data = b"e+10"
        match_context = DummyMatchContext(data)
        match_element = decimal_float_value_me.get_match_element(self.path, match_context)
        self.compare_no_match_results(data, match_element, match_context)

    def test5get_match_element_mandatory_blank_values(self):
        """Test valid float values with "mandatory" or "blank" values of value_sign_type, value_pad_type and exponent_type."""
        decimal_float_value_me = DecimalFloatValueModelElement(
            self.id_, DecimalFloatValueModelElement.SIGN_TYPE_MANDATORY, DecimalFloatValueModelElement.PAD_TYPE_BLANK,
            DecimalFloatValueModelElement.EXP_TYPE_MANDATORY)
        data = b"+22.25 some string."
        value = b"+22.25"
        match_context = DummyMatchContext(data)
        match_element = decimal_float_value_me.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, value, 22.25, None)

        data = b"-22.25 some string."
        value = b"-22.25"
        match_context = DummyMatchContext(data)
        match_element = decimal_float_value_me.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, value, -22.25, None)

        data = b"+0.25 some string."
        value = b"+0.25"
        match_context = DummyMatchContext(data)
        match_element = decimal_float_value_me.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, value, 0.25, None)

        data = b"+22 some string."
        value = b"+22"
        match_context = DummyMatchContext(data)
        match_element = decimal_float_value_me.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, value, 22, None)

        data = b"+22. some string"
        value = b"+22."
        match_context = DummyMatchContext(data)
        match_element = decimal_float_value_me.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, value, 22.0, None)

        data = b"+ 25 some string"
        value = b"+ 25"
        match_context = DummyMatchContext(data)
        match_element = decimal_float_value_me.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, value, 25, None)

        data = b"- 25 some string"
        value = b"- 25"
        match_context = DummyMatchContext(data)
        match_element = decimal_float_value_me.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, value, -25, None)

        data = b"+1e-5 some string"
        value = b"+1e-5"
        match_context = DummyMatchContext(data)
        match_element = decimal_float_value_me.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, value, 1e-5, None)

        data = b"+1e+0 some string"
        value = b"+1e+0"
        match_context = DummyMatchContext(data)
        match_element = decimal_float_value_me.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, value, 1, None)

        data = b"+ 1e+0 some string"
        value = b"+ 1e+0"
        match_context = DummyMatchContext(data)
        match_element = decimal_float_value_me.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, value, 1, None)

        data = b"+0 some string"
        value = b"+0"
        match_context = DummyMatchContext(data)
        match_element = decimal_float_value_me.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, value, 0, None)

    def test6get_match_element_mandatory_blank_values_no_match(self):
        """Test not matching values with default values of value_sign_type, value_pad_type and exponent_type."""
        decimal_float_value_me = DecimalFloatValueModelElement(
            self.id_, DecimalFloatValueModelElement.SIGN_TYPE_MANDATORY, DecimalFloatValueModelElement.PAD_TYPE_BLANK,
            DecimalFloatValueModelElement.EXP_TYPE_MANDATORY)
        data = b"22.25"
        match_context = DummyMatchContext(data)
        match_element = decimal_float_value_me.get_match_element(self.path, match_context)
        self.compare_no_match_results(data, match_element, match_context)

        data = b"+  22.25"
        match_context = DummyMatchContext(data)
        match_element = decimal_float_value_me.get_match_element(self.path, match_context)
        self.compare_no_match_results(data, match_element, match_context)

        data = b"-  22.25"
        match_context = DummyMatchContext(data)
        match_element = decimal_float_value_me.get_match_element(self.path, match_context)
        self.compare_no_match_results(data, match_element, match_context)

        data = b"+22,25"
        value = b"+22"
        match_context = DummyMatchContext(data)
        match_element = decimal_float_value_me.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, value, 22, None)

        data = b"22,25"
        match_context = DummyMatchContext(data)
        match_element = decimal_float_value_me.get_match_element(self.path, match_context)
        self.compare_no_match_results(data, match_element, match_context)

        data = b"22.12.2021 some string."
        match_context = DummyMatchContext(data)
        match_element = decimal_float_value_me.get_match_element(self.path, match_context)
        self.compare_no_match_results(data, match_element, match_context)

        data = b".25"
        match_context = DummyMatchContext(data)
        match_element = decimal_float_value_me.get_match_element(self.path, match_context)
        self.compare_no_match_results(data, match_element, match_context)

        data = b" +25"
        match_context = DummyMatchContext(data)
        match_element = decimal_float_value_me.get_match_element(self.path, match_context)
        self.compare_no_match_results(data, match_element, match_context)

        data = b" -25"
        match_context = DummyMatchContext(data)
        match_element = decimal_float_value_me.get_match_element(self.path, match_context)
        self.compare_no_match_results(data, match_element, match_context)

        data = b"025"
        match_context = DummyMatchContext(data)
        match_element = decimal_float_value_me.get_match_element(self.path, match_context)
        self.compare_no_match_results(data, match_element, match_context)

        data = b"0025"
        match_context = DummyMatchContext(data)
        match_element = decimal_float_value_me.get_match_element(self.path, match_context)
        self.compare_no_match_results(data, match_element, match_context)

        data = b"e+10"
        match_context = DummyMatchContext(data)
        match_element = decimal_float_value_me.get_match_element(self.path, match_context)
        self.compare_no_match_results(data, match_element, match_context)

        data = b"00"
        match_context = DummyMatchContext(data)
        match_element = decimal_float_value_me.get_match_element(self.path, match_context)
        self.compare_no_match_results(data, match_element, match_context)

    def test7element_id_input_validation(self):
        """Check if element_id is validated."""
        self.assertRaises(ValueError, DecimalFloatValueModelElement, "")  # empty element_id
        self.assertRaises(TypeError, DecimalFloatValueModelElement, None)  # None element_id
        self.assertRaises(TypeError, DecimalFloatValueModelElement, b"path")  # bytes element_id is not allowed
        self.assertRaises(TypeError, DecimalFloatValueModelElement, True)  # bool element_id is not allowed
        self.assertRaises(TypeError, DecimalFloatValueModelElement, 123)  # integer element_id is not allowed
        self.assertRaises(TypeError, DecimalFloatValueModelElement, 123.22)  # float element_id is not allowed
        self.assertRaises(TypeError, DecimalFloatValueModelElement, {"id": "path"})  # dict element_id is not allowed
        self.assertRaises(TypeError, DecimalFloatValueModelElement, ["path"])  # list element_id is not allowed
        self.assertRaises(TypeError, DecimalFloatValueModelElement, [])  # empty list element_id is not allowed
        self.assertRaises(TypeError, DecimalFloatValueModelElement, ())  # empty tuple element_id is not allowed
        self.assertRaises(TypeError, DecimalFloatValueModelElement, set())  # empty set element_id is not allowed

    def test8value_sign_type_input_validation(self):
        """Check if value_sign_type is validated."""
        DecimalFloatValueModelElement(self.id_, value_sign_type="none")
        DecimalFloatValueModelElement(self.id_, value_sign_type="optional")
        DecimalFloatValueModelElement(self.id_, value_sign_type="mandatory")

        self.assertRaises(ValueError, DecimalFloatValueModelElement, self.id_, value_sign_type="None")
        self.assertRaises(TypeError, DecimalFloatValueModelElement, self.id_, value_sign_type=None)
        self.assertRaises(TypeError, DecimalFloatValueModelElement, self.id_, value_sign_type=b"none")
        self.assertRaises(TypeError, DecimalFloatValueModelElement, self.id_, value_sign_type=True)
        self.assertRaises(TypeError, DecimalFloatValueModelElement, self.id_, value_sign_type=123)
        self.assertRaises(TypeError, DecimalFloatValueModelElement, self.id_, value_sign_type=123.22)
        self.assertRaises(TypeError, DecimalFloatValueModelElement, self.id_, value_sign_type={"value_sign_type": "none"})
        self.assertRaises(TypeError, DecimalFloatValueModelElement, self.id_, value_sign_type=["none"])
        self.assertRaises(TypeError, DecimalFloatValueModelElement, self.id_, value_sign_type=[])
        self.assertRaises(TypeError, DecimalFloatValueModelElement, self.id_, value_sign_type=())
        self.assertRaises(TypeError, DecimalFloatValueModelElement, self.id_, value_sign_type=set())

    def test9value_pad_type_input_validation(self):
        """Check if value_pad_type is validated."""
        DecimalFloatValueModelElement(self.id_, value_pad_type="none")
        DecimalFloatValueModelElement(self.id_, value_pad_type="zero")
        DecimalFloatValueModelElement(self.id_, value_pad_type="blank")

        self.assertRaises(ValueError, DecimalFloatValueModelElement, self.id_, value_pad_type="None")
        self.assertRaises(TypeError, DecimalFloatValueModelElement, self.id_, value_pad_type=None)
        self.assertRaises(TypeError, DecimalFloatValueModelElement, self.id_, value_pad_type=b"none")
        self.assertRaises(TypeError, DecimalFloatValueModelElement, self.id_, value_pad_type=True)
        self.assertRaises(TypeError, DecimalFloatValueModelElement, self.id_, value_pad_type=123)
        self.assertRaises(TypeError, DecimalFloatValueModelElement, self.id_, value_pad_type=123.22)
        self.assertRaises(TypeError, DecimalFloatValueModelElement, self.id_, value_pad_type={"value_sign_type": "none"})
        self.assertRaises(TypeError, DecimalFloatValueModelElement, self.id_, value_pad_type=["none"])
        self.assertRaises(TypeError, DecimalFloatValueModelElement, self.id_, value_pad_type=[])
        self.assertRaises(TypeError, DecimalFloatValueModelElement, self.id_, value_pad_type=())
        self.assertRaises(TypeError, DecimalFloatValueModelElement, self.id_, value_pad_type=set())

    def test10exponent_type_input_validation(self):
        """Check if exponent_type is validated."""
        DecimalFloatValueModelElement(self.id_, exponent_type="none")
        DecimalFloatValueModelElement(self.id_, exponent_type="optional")
        DecimalFloatValueModelElement(self.id_, exponent_type="mandatory")

        self.assertRaises(ValueError, DecimalFloatValueModelElement, self.id_, exponent_type="None")
        self.assertRaises(TypeError, DecimalFloatValueModelElement, self.id_, exponent_type=None)
        self.assertRaises(TypeError, DecimalFloatValueModelElement, self.id_, exponent_type=b"none")
        self.assertRaises(TypeError, DecimalFloatValueModelElement, self.id_, exponent_type=True)
        self.assertRaises(TypeError, DecimalFloatValueModelElement, self.id_, exponent_type=123)
        self.assertRaises(TypeError, DecimalFloatValueModelElement, self.id_, exponent_type=123.22)
        self.assertRaises(TypeError, DecimalFloatValueModelElement, self.id_, exponent_type={"value_sign_type": "none"})
        self.assertRaises(TypeError, DecimalFloatValueModelElement, self.id_, exponent_type=["none"])
        self.assertRaises(TypeError, DecimalFloatValueModelElement, self.id_, exponent_type=[])
        self.assertRaises(TypeError, DecimalFloatValueModelElement, self.id_, exponent_type=())
        self.assertRaises(TypeError, DecimalFloatValueModelElement, self.id_, exponent_type=set())

    def test11get_match_element_match_context_input_validation(self):
        """Check if an exception is raised, when other classes than MatchContext are used in get_match_element."""
        model_element = DecimalFloatValueModelElement(self.id_)
        data = b"123.22"
        model_element.get_match_element(self.path, DummyMatchContext(data))
        model_element.get_match_element(self.path, MatchContext(data))

        self.assertRaises(AttributeError, model_element.get_match_element, self.path, MatchElement(self.path, data, None, None))
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
