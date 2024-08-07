import unittest
from aminer.parsing.HexStringModelElement import HexStringModelElement
from aminer.parsing.MatchContext import MatchContext
from aminer.parsing.MatchElement import MatchElement
from unit.TestBase import TestBase, DummyMatchContext


class HexStringModelElementTest(TestBase):
    """Unittests for the HexStringModelElement."""

    id_ = "hex"
    path = "path"

    def test1get_match_element_valid_match(self):
        """Try all values and check if the desired results are produced."""
        allowed_chars = [b"0", b"1", b"2", b"3", b"4", b"5", b"6", b"7", b"8", b"9", b"a", b"b", b"c", b"d", b"e", b"f"]
        char1 = b"\x00"
        char2 = b"\x00"
        hex_string_model_element = HexStringModelElement(self.id_)

        while ord(char2) < ord(b"\x7F"):
            data = char2 + char1
            match_context = DummyMatchContext(data)
            match_element = hex_string_model_element.get_match_element(self.path, match_context)
            if char2 in allowed_chars:
                if char1 in allowed_chars:
                    match_context.match_string = bytes.fromhex(data.decode())  # match_context.match_string check has to be skipped.
                    match_context.match_data = data[len(match_context.match_string):]  # match_context.match_data has to be rewritten.
                    self.compare_match_results(
                        data, match_element, match_context, self.id_, self.path, bytes.fromhex(data.decode()), data, None)
                    self.assertEqual(match_element.get_match_object(), data)
                else:
                    match_context.match_string = bytes.fromhex("0" + char2.decode())  # match_context.match_string check has to be skipped.
                    self.compare_match_results(
                        data, match_element, match_context, self.id_, self.path, bytes.fromhex("0" + char2.decode()), char2, None)
                    self.assertEqual(match_element.get_match_object(), char2)
            else:
                self.compare_no_match_results(data, match_element, match_context)
            if ord(char1) == 0x7f:
                char1 = b"\x00"
                char2 = bytes(chr(ord(char2) + 1), "utf-8")
            else:
                char1 = bytes(chr(ord(char1) + 1), "utf-8")

        allowed_chars = [b"0", b"1", b"2", b"3", b"4", b"5", b"6", b"7", b"8", b"9", b"A", b"B", b"C", b"D", b"E", b"F"]
        char1 = b"\x00"
        char2 = b"\x00"
        hex_string_model_element = HexStringModelElement(self.id_, True)

        while ord(char2) < ord(b"\x7F"):
            data = char2 + char1
            match_context = DummyMatchContext(data)
            match_element = hex_string_model_element.get_match_element(self.path, match_context)
            if char2 in allowed_chars:
                if char1 in allowed_chars:
                    self.assertEqual(match_element.get_match_object(), data)
                else:
                    self.assertEqual(match_element.get_match_object(), char2)
            else:
                self.compare_no_match_results(data, match_element, match_context)
            if ord(char1) == 0x7f:
                char1 = b"\x00"
                char2 = bytes(chr(ord(char2) + 1), "utf-8")
            else:
                char1 = bytes(chr(ord(char1) + 1), "utf-8")

    def test2get_match_element_no_match(self):
        """Parse not matching substring from MatchContext and check if the MatchContext was not changed."""
        data = b""
        match_context = DummyMatchContext(data)
        hex_me = HexStringModelElement(self.id_)
        match_element = hex_me.get_match_element(self.path, match_context)
        self.compare_no_match_results(data, match_element, match_context)

    def test3element_id_input_validation(self):
        """Check if element_id is validated."""
        self.assertRaises(ValueError, HexStringModelElement, "")  # empty element_id
        self.assertRaises(TypeError, HexStringModelElement, None)  # None element_id
        self.assertRaises(TypeError, HexStringModelElement, b"path")  # bytes element_id is not allowed
        self.assertRaises(TypeError, HexStringModelElement, True)  # boolean element_id is not allowed
        self.assertRaises(TypeError, HexStringModelElement, 123)  # integer element_id is not allowed
        self.assertRaises(TypeError, HexStringModelElement, 123.22)  # float element_id is not allowed
        self.assertRaises(TypeError, HexStringModelElement, {"id": "path"})  # dict element_id is not allowed
        self.assertRaises(TypeError, HexStringModelElement, ["path"])  # list element_id is not allowed
        self.assertRaises(TypeError, HexStringModelElement, [])  # empty list element_id is not allowed
        self.assertRaises(TypeError, HexStringModelElement, ())  # empty tuple element_id is not allowed
        self.assertRaises(TypeError, HexStringModelElement, set())  # empty set element_id is not allowed

    def test4upper_case_input_validation(self):
        """Check if element_id is validated."""
        self.assertRaises(TypeError, HexStringModelElement, self.id_, "path")  # string upper_case
        self.assertRaises(TypeError, HexStringModelElement, self.id_, None)  # None upper_case
        self.assertRaises(TypeError, HexStringModelElement, self.id_, b"path")  # bytes upper_case is not allowed
        self.assertRaises(TypeError, HexStringModelElement, self.id_, 123)  # integer upper_case is not allowed
        self.assertRaises(TypeError, HexStringModelElement, self.id_, 123.22)  # float upper_case is not allowed
        self.assertRaises(TypeError, HexStringModelElement, self.id_, {"id": "path"})  # dict upper_case is not allowed
        self.assertRaises(TypeError, HexStringModelElement, self.id_, ["path"])  # list upper_case is not allowed
        self.assertRaises(TypeError, HexStringModelElement, self.id_, [])  # empty list upper_case is not allowed
        self.assertRaises(TypeError, HexStringModelElement, self.id_, ())  # empty tuple upper_case is not allowed
        self.assertRaises(TypeError, HexStringModelElement, self.id_, set())  # empty set upper_case is not allowed

    def test5get_match_element_match_context_input_validation(self):
        """Check if an exception is raised, when other classes than MatchContext are used in get_match_element."""
        model_element = HexStringModelElement(self.id_)
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

    def test6performance(self):
        """Test the performance of the implementation. Comment this test out in normal cases."""
        import_setup = """
import copy
from unit.TestBase import DummyMatchContext
from aminer.parsing.HexStringModelElement import HexStringModelElement
times = 100000
"""
        string_short_setup = """
hex_string = b"100"
"""
        string_long_setup = """
hex_string = b"23999EA30A3430DA"
"""
        end_setup = """
dummy_match_context = DummyMatchContext(hex_string)
dummy_match_context_list = [copy.deepcopy(dummy_match_context) for _ in range(times)]
hex_string_dme = HexStringModelElement("s0")

def run():
    match_context = dummy_match_context_list.pop(0)
    hex_string_dme.get_match_element("hex", match_context)
"""
        _setup_short = import_setup + string_short_setup + end_setup
        _setup_long = import_setup + string_long_setup + end_setup
        # import timeit
        # times = 100000
        # print("Every hex string is run 100.000 times.")
        # t = timeit.timeit(setup=_setup_short, stmt="run()", number=times)
        # print("Hex string 100: ", t)
        # t = timeit.timeit(setup=_setup_long, stmt="run()", number=times)
        # print("Hex string 23999EA30A3430DA: ", t)


if __name__ == "__main__":
    unittest.main()
