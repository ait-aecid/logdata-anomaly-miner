import unittest
import time
from unit.TestBase import TestBase, DummyMatchContext, DummyFixedDataModelElement, DummyFirstMatchModelElement
from aminer.analysis.MatchFilter import MatchFilter
from aminer.input.LogAtom import LogAtom
from aminer.parsing.ParserMatch import ParserMatch
from datetime import datetime


class MatchFilterTest(TestBase):
    """Unittests for the MatchFilter."""

    def test1receive_atom(self):
        """Test if log atoms are processed correctly."""
        fmme = DummyFirstMatchModelElement("first", [DummyFixedDataModelElement(f"s{i}", f"val{i}".encode()) for i in range(10)])
        match_filter = MatchFilter(self.aminer_config, [f"/first/s{i}" for i in range(10)], [self.stream_printer_event_handler])
        t = time.time()
        expected_string = '%s Log Atom Filtered\nMatchFilter: "None" (1 lines)\n  val%d\n\n'

        # check if an event is triggered if the path is in the target_path_list.
        for val in range(10):
            val_str = f"val{val}".encode()
            log_atom = LogAtom(val_str, ParserMatch(fmme.get_match_element("", DummyMatchContext(val_str))), t, match_filter)
            match_filter.receive_atom(log_atom)
            self.assertEqual(expected_string % (datetime.fromtimestamp(t).strftime("%Y-%m-%d %H:%M:%S"), val), self.output_stream.getvalue())
            self.reset_output_stream()

        # check if an event is not triggered if the path is not in the target_path_list.
        match_filter.target_path_list =  ["/strings"]
        for val in range(10):
            val_str = f"val{val}".encode()
            log_atom = LogAtom(val_str, ParserMatch(fmme.get_match_element("", DummyMatchContext(val_str))), t, match_filter)
            match_filter.receive_atom(log_atom)
            self.assertEqual("", self.output_stream.getvalue())

        # check if an event is triggered, when the path is in the target_path_list and the value is in the target_value_list.
        match_filter.target_path_list = [f"/first/s{i}" for i in range(10)]
        match_filter.target_value_list = [f"val{i}" for i in range(10)]
        for val in range(10):
            val_str = f"val{val}".encode()
            log_atom = LogAtom(val_str, ParserMatch(fmme.get_match_element("", DummyMatchContext(val_str))), t, match_filter)
            match_filter.receive_atom(log_atom)
            self.assertEqual(expected_string % (datetime.fromtimestamp(t).strftime("%Y-%m-%d %H:%M:%S"), val), self.output_stream.getvalue())
            self.reset_output_stream()

        # check if an event is not triggered when the path is in the target_path_list and the value is not in the target_value_list.
        match_filter.target_value_list = [f"val{i}" for i in range(6)]
        for val in range(10):
            val_str = f"val{val}".encode()
            log_atom = LogAtom(val_str, ParserMatch(fmme.get_match_element("", DummyMatchContext(val_str))), t, match_filter)
            match_filter.receive_atom(log_atom)
            if val <= 5:
                self.assertEqual(expected_string % (datetime.fromtimestamp(t).strftime("%Y-%m-%d %H:%M:%S"), val), self.output_stream.getvalue())
            else:
                self.assertEqual("", self.output_stream.getvalue())
            self.reset_output_stream()

    def test2validate_parameters(self):
        """Test all initialization parameters for the detector. Input parameters must be validated in the class."""
        self.assertRaises(ValueError, MatchFilter, self.aminer_config, [], [self.stream_printer_event_handler])
        self.assertRaises(TypeError, MatchFilter, self.aminer_config, None, [self.stream_printer_event_handler])
        self.assertRaises(TypeError, MatchFilter, self.aminer_config, "", [self.stream_printer_event_handler])
        self.assertRaises(TypeError, MatchFilter, self.aminer_config, b"Default", [self.stream_printer_event_handler])
        self.assertRaises(TypeError, MatchFilter, self.aminer_config, True, [self.stream_printer_event_handler])
        self.assertRaises(TypeError, MatchFilter, self.aminer_config, 123, [self.stream_printer_event_handler])
        self.assertRaises(TypeError, MatchFilter, self.aminer_config, 123.3, [self.stream_printer_event_handler])
        self.assertRaises(TypeError, MatchFilter, self.aminer_config, {"id": "Default"}, [self.stream_printer_event_handler])
        self.assertRaises(TypeError, MatchFilter, self.aminer_config, (), [self.stream_printer_event_handler])
        self.assertRaises(TypeError, MatchFilter, self.aminer_config, set(), [self.stream_printer_event_handler])

        self.assertRaises(TypeError, MatchFilter, self.aminer_config, ["Default"], ["default"])
        self.assertRaises(TypeError, MatchFilter, self.aminer_config, ["Default"], None)
        self.assertRaises(TypeError, MatchFilter, self.aminer_config, ["Default"], "")
        self.assertRaises(TypeError, MatchFilter, self.aminer_config, ["Default"], b"Default")
        self.assertRaises(TypeError, MatchFilter, self.aminer_config, ["Default"], True)
        self.assertRaises(TypeError, MatchFilter, self.aminer_config, ["Default"], 123)
        self.assertRaises(TypeError, MatchFilter, self.aminer_config, ["Default"], 123.3)
        self.assertRaises(TypeError, MatchFilter, self.aminer_config, ["Default"], {"id": "Default"})
        self.assertRaises(TypeError, MatchFilter, self.aminer_config, ["Default"], ())
        self.assertRaises(TypeError, MatchFilter, self.aminer_config, ["Default"], set())

        # target_value_list can actually be empty with [] or None.
        self.assertRaises(ValueError, MatchFilter, self.aminer_config, ["Default"], [self.stream_printer_event_handler], [""])
        self.assertRaises(TypeError, MatchFilter, self.aminer_config, ["Default"], [self.stream_printer_event_handler], [b"default"])
        self.assertRaises(TypeError, MatchFilter, self.aminer_config, ["Default"], [self.stream_printer_event_handler], True)
        self.assertRaises(TypeError, MatchFilter, self.aminer_config, ["Default"], [self.stream_printer_event_handler], 123)
        self.assertRaises(TypeError, MatchFilter, self.aminer_config, ["Default"], [self.stream_printer_event_handler], 123.3)
        self.assertRaises(TypeError, MatchFilter, self.aminer_config, ["Default"], [self.stream_printer_event_handler], {"id": "Default"})
        self.assertRaises(TypeError, MatchFilter, self.aminer_config, ["Default"], [self.stream_printer_event_handler], ())
        self.assertRaises(TypeError, MatchFilter, self.aminer_config, ["Default"], [self.stream_printer_event_handler], set())

        self.assertRaises(TypeError, MatchFilter, self.aminer_config, ["Default"], [self.stream_printer_event_handler], output_logline="")
        self.assertRaises(TypeError, MatchFilter, self.aminer_config, ["Default"], [self.stream_printer_event_handler], output_logline=None)
        self.assertRaises(TypeError, MatchFilter, self.aminer_config, ["Default"], [self.stream_printer_event_handler], output_logline=b"Default")
        self.assertRaises(TypeError, MatchFilter, self.aminer_config, ["Default"], [self.stream_printer_event_handler], output_logline=["default"])
        self.assertRaises(TypeError, MatchFilter, self.aminer_config, ["Default"], [self.stream_printer_event_handler], output_logline=123)
        self.assertRaises(TypeError, MatchFilter, self.aminer_config, ["Default"], [self.stream_printer_event_handler], output_logline=123.3)
        self.assertRaises(TypeError, MatchFilter, self.aminer_config, ["Default"], [self.stream_printer_event_handler], output_logline={"id": "Default"})
        self.assertRaises(TypeError, MatchFilter, self.aminer_config, ["Default"], [self.stream_printer_event_handler], output_logline=())
        self.assertRaises(TypeError, MatchFilter, self.aminer_config, ["Default"], [self.stream_printer_event_handler], output_logline=set())
        MatchFilter(self.aminer_config, ["Default"], [self.stream_printer_event_handler], ["val"], True)


if __name__ == "__main__":
    unittest.main()
