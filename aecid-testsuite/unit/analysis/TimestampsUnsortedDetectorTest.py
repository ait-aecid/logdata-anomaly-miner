import unittest
from aminer.input.LogAtom import LogAtom
from aminer.parsing.ParserMatch import ParserMatch
import time
from aminer.analysis.TimestampsUnsortedDetector import TimestampsUnsortedDetector
from aminer.analysis.NewMatchPathDetector import NewMatchPathDetector
from unit.TestBase import TestBase, DummyFixedDataModelElement, DummyMatchContext
from datetime import datetime


class TimestampsUnsortedDetectorTest(TestBase):
    """Unittests for the TimestampsUnsortedDetector."""

    def test1receive_atom(self):
        """Test if log atoms are processed correctly and the detector is learning the correct timestamps."""
        __expected_string = '%s Timestamp %s below %s\n%s: "%s" (%d lines)\n  %s\n\n'
        pid = b" pid="
        datetime_format_string = "%Y-%m-%d %H:%M:%S"

        # test if nothing happens, when the timestamp is, as expected, higher than the last one.
        description = "Test1TimestampsUnsortedDetector"
        match_context_fixed_dme = DummyMatchContext(pid)
        fixed_dme = DummyFixedDataModelElement("s1", pid)
        match_element_fixed_dme = fixed_dme.get_match_element("match", match_context_fixed_dme)
        new_match_path_detector = NewMatchPathDetector(self.aminer_config, [self.stream_printer_event_handler], "Default", False)
        self.analysis_context.register_component(new_match_path_detector, description + "2")

        t = time.time()
        log_atom = LogAtom(fixed_dme.data, ParserMatch(match_element_fixed_dme), t, new_match_path_detector)
        timestamp_unsorted_detector = TimestampsUnsortedDetector(self.aminer_config, [self.stream_printer_event_handler], False, False)
        self.analysis_context.register_component(timestamp_unsorted_detector, description)
        self.assertTrue(timestamp_unsorted_detector.receive_atom(log_atom))
        self.assertEqual(self.output_stream.getvalue(), "")

        log_atom.set_timestamp(t + 10000)
        self.assertTrue(timestamp_unsorted_detector.receive_atom(log_atom))
        self.assertEqual(self.output_stream.getvalue(), "")

        # test if an event is created, when the timestamp is lower than the last one.
        log_atom.set_timestamp(t)
        self.assertTrue(timestamp_unsorted_detector.receive_atom(log_atom))
        self.assertEqual(self.output_stream.getvalue(), __expected_string % (
            datetime.fromtimestamp(t).strftime(datetime_format_string), datetime.fromtimestamp(t).strftime(datetime_format_string),
            datetime.fromtimestamp(t + 10000).strftime(datetime_format_string), timestamp_unsorted_detector.__class__.__name__, description, 1, " pid="))
        self.reset_output_stream()

        # test if the aminer exits, when the timestamp is lower than the last one and the exit_on_error_flag is set.
        timestamp_unsorted_detector.exit_on_error_flag = True
        log_atom.set_timestamp(t - 10000)
        with self.assertRaises(SystemExit) as cm:
            timestamp_unsorted_detector.receive_atom(log_atom)
        self.assertEqual(cm.exception.code, 1)
        self.assertEqual(self.output_stream.getvalue(), __expected_string % (
            datetime.fromtimestamp(t - 10000).strftime(datetime_format_string), datetime.fromtimestamp(t - 10000).strftime(datetime_format_string),
            datetime.fromtimestamp(t).strftime(datetime_format_string), timestamp_unsorted_detector.__class__.__name__, description, 1, " pid="))
        self.reset_output_stream()

    def test2validate_parameters(self):
        """Test all initialization parameters for the detector. Input parameters must be validated in the class."""
        self.assertRaises(ValueError, TimestampsUnsortedDetector, self.aminer_config, [])
        self.assertRaises(TypeError, TimestampsUnsortedDetector, self.aminer_config, ["default"])
        self.assertRaises(TypeError, TimestampsUnsortedDetector, self.aminer_config, None)
        self.assertRaises(TypeError, TimestampsUnsortedDetector, self.aminer_config, "")
        self.assertRaises(TypeError, TimestampsUnsortedDetector, self.aminer_config, b"Default")
        self.assertRaises(TypeError, TimestampsUnsortedDetector, self.aminer_config, True)
        self.assertRaises(TypeError, TimestampsUnsortedDetector, self.aminer_config, 123)
        self.assertRaises(TypeError, TimestampsUnsortedDetector, self.aminer_config, 123.3)
        self.assertRaises(TypeError, TimestampsUnsortedDetector, self.aminer_config, {"id": "Default"})
        self.assertRaises(TypeError, TimestampsUnsortedDetector, self.aminer_config, ())
        self.assertRaises(TypeError, TimestampsUnsortedDetector, self.aminer_config, set())

        self.assertRaises(TypeError, TimestampsUnsortedDetector, self.aminer_config, [self.stream_printer_event_handler], exit_on_error_flag=b"True")
        self.assertRaises(TypeError, TimestampsUnsortedDetector, self.aminer_config, [self.stream_printer_event_handler], exit_on_error_flag="True")
        self.assertRaises(TypeError, TimestampsUnsortedDetector, self.aminer_config, [self.stream_printer_event_handler], exit_on_error_flag=123)
        self.assertRaises(TypeError, TimestampsUnsortedDetector, self.aminer_config, [self.stream_printer_event_handler], exit_on_error_flag=123.22)
        self.assertRaises(TypeError, TimestampsUnsortedDetector, self.aminer_config, [self.stream_printer_event_handler], exit_on_error_flag={"id": "Default"})
        self.assertRaises(TypeError, TimestampsUnsortedDetector, self.aminer_config, [self.stream_printer_event_handler], exit_on_error_flag=["Default"])
        self.assertRaises(TypeError, TimestampsUnsortedDetector, self.aminer_config, [self.stream_printer_event_handler], exit_on_error_flag=[])
        self.assertRaises(TypeError, TimestampsUnsortedDetector, self.aminer_config, [self.stream_printer_event_handler], exit_on_error_flag=())
        self.assertRaises(TypeError, TimestampsUnsortedDetector, self.aminer_config, [self.stream_printer_event_handler], exit_on_error_flag=set())
        TimestampsUnsortedDetector(self.aminer_config, [self.stream_printer_event_handler], exit_on_error_flag=True)

        self.assertRaises(TypeError, TimestampsUnsortedDetector, self.aminer_config, [self.stream_printer_event_handler], output_logline=None)
        self.assertRaises(TypeError, TimestampsUnsortedDetector, self.aminer_config, [self.stream_printer_event_handler], output_logline=b"True")
        self.assertRaises(TypeError, TimestampsUnsortedDetector, self.aminer_config, [self.stream_printer_event_handler], output_logline="True")
        self.assertRaises(TypeError, TimestampsUnsortedDetector, self.aminer_config, [self.stream_printer_event_handler], output_logline=123)
        self.assertRaises(TypeError, TimestampsUnsortedDetector, self.aminer_config, [self.stream_printer_event_handler], output_logline=123.22)
        self.assertRaises(TypeError, TimestampsUnsortedDetector, self.aminer_config, [self.stream_printer_event_handler], output_logline={"id": "Default"})
        self.assertRaises(TypeError, TimestampsUnsortedDetector, self.aminer_config, [self.stream_printer_event_handler], output_logline=["Default"])
        self.assertRaises(TypeError, TimestampsUnsortedDetector, self.aminer_config, [self.stream_printer_event_handler], output_logline=[])
        self.assertRaises(TypeError, TimestampsUnsortedDetector, self.aminer_config, [self.stream_printer_event_handler], output_logline=())
        self.assertRaises(TypeError, TimestampsUnsortedDetector, self.aminer_config, [self.stream_printer_event_handler], output_logline=set())
        TimestampsUnsortedDetector(self.aminer_config, [self.stream_printer_event_handler], output_logline=True)


if __name__ == "__main__":
    unittest.main()
