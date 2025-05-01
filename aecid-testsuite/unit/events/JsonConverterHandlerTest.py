import time
import unittest
from aminer.events.JsonConverterHandler import JsonConverterHandler
from aminer.input.LogAtom import LogAtom
from aminer.parsing.ParserMatch import ParserMatch
from unit.TestBase import TestBase, DummyFixedDataModelElement, DummyMatchContext


class JsonConverterHandlerTest(TestBase):
    """Unittests for the JsonConverterHandler."""

    maxDiff = None
    output_logline = True
    resource_name = b"testresource"
    persistence_id = "Default"

    def test1receive_event(self):
        """Test if events are processed correctly and that edge cases are caught in exceptions."""
        match_context = DummyMatchContext(b" pid=")
        fdme = DummyFixedDataModelElement("s1", b" pid=")
        match_element = fdme.get_match_element("match", match_context)
        t = time.time()

        test = "Analysis.TestDetector"
        event_message = "An event happened!"
        sorted_log_lines = ["Event happened at /path/ 5 times.", "", "", "", ""]
        description = "jsonConverterHandlerDescription"
        expected_string = '{\n  "AnalysisComponent": {\n    "AnalysisComponentIdentifier": 0,\n    "AnalysisComponentType": "%s",\n    ' \
                          '"AnalysisComponentName": "%s",\n    "Message": "%s",\n    "PersistenceFileName": "%s",\n    "AffectedParserPaths":' \
                          ' [\n      "test/path/1",\n      "test/path/2"\n    ],\n    "LogResource": "testresource"\n  },\n  "LogData": ' \
                          '{\n    "RawLogData": [\n      " pid="\n    ],\n    "Timestamps": [\n      %s\n    ],\n    "DetectionTimestamp":' \
                          ' %s,\n    "LogLinesCount": 5,\n    "AnnotatedMatchElement": {\n      "match/s1": " pid="\n    }\n  }%s\n}\n'

        jch = JsonConverterHandler([self.stream_printer_event_handler], self.analysis_context)
        log_atom = LogAtom(fdme.data, ParserMatch(match_element), t, self)
        self.analysis_context.register_component(self, description)
        event_data = {"AnalysisComponent": {"AffectedParserPaths": ["test/path/1", "test/path/2"]}}
        jch.receive_event(test, event_message, sorted_log_lines, event_data, log_atom, self)
        detection_timestamp = None
        for line in self.output_stream.getvalue().split("\n"):
            if "DetectionTimestamp" in line:
                detection_timestamp = line.split(":")[1].strip(" ,")
        self.assertEqual(self.output_stream.getvalue(), expected_string % (self.__class__.__name__, description, event_message, self.persistence_id, round(t, 2), detection_timestamp, ""))
        self.reset_output_stream()

        # test output_event_handlers
        self.output_event_handlers = []
        self.assertTrue(jch.receive_event(test, event_message, sorted_log_lines, event_data, log_atom, self))
        self.assertEqual(self.output_stream.getvalue(), "")

        self.output_event_handlers = [jch]
        self.assertTrue(jch.receive_event(test, event_message, sorted_log_lines, event_data, log_atom, self))
        val = self.output_stream.getvalue()
        if val.endswith("\n\n"):
            val = val[:-1]
        detection_timestamp = None
        for line in val.split("\n"):
            if "DetectionTimestamp" in line:
                detection_timestamp = line.split(":")[1].strip(" ,")
                break
        self.assertEqual(val, expected_string % (self.__class__.__name__, description, event_message, self.persistence_id, round(t, 2), detection_timestamp, ""))
        self.reset_output_stream()

        # test suppress detector list
        self.output_event_handlers = None
        self.analysis_context.suppress_detector_list = [description]
        self.assertTrue(jch.receive_event(test, event_message, sorted_log_lines, event_data, log_atom, self))
        self.assertEqual(self.output_stream.getvalue(), "")

        self.output_event_handlers = [jch]
        self.analysis_context.suppress_detector_list = []
        self.assertTrue(jch.receive_event(test, event_message, sorted_log_lines, event_data, log_atom, self))
        self.assertEqual(val, expected_string % (self.__class__.__name__, description, event_message, self.persistence_id, round(t, 2), detection_timestamp, ""))

    def test2validate_parameters(self):
        """Test all initialization parameters for the event handler. Input parameters must be validated in the class."""
        JsonConverterHandler([self.stream_printer_event_handler], self.analysis_context)
        self.assertRaises(TypeError, JsonConverterHandler, ["default"], self.analysis_context)
        self.assertRaises(TypeError, JsonConverterHandler, None, self.analysis_context)
        self.assertRaises(TypeError, JsonConverterHandler, "Default", self.analysis_context)
        self.assertRaises(TypeError, JsonConverterHandler, b"Default", self.analysis_context)
        self.assertRaises(TypeError, JsonConverterHandler, True, self.analysis_context)
        self.assertRaises(TypeError, JsonConverterHandler, 123, self.analysis_context)
        self.assertRaises(TypeError, JsonConverterHandler, 123.3, self.analysis_context)
        self.assertRaises(TypeError, JsonConverterHandler, {"id": "Default"}, self.analysis_context)
        self.assertRaises(TypeError, JsonConverterHandler, (), self.analysis_context)
        self.assertRaises(TypeError, JsonConverterHandler, set(), self.analysis_context)
        self.assertRaises(ValueError, JsonConverterHandler, [], self.analysis_context)

        self.assertRaises(TypeError, JsonConverterHandler, [self.stream_printer_event_handler], self.analysis_context, ["default"])
        self.assertRaises(TypeError, JsonConverterHandler, [self.stream_printer_event_handler], self.analysis_context, None)
        self.assertRaises(TypeError, JsonConverterHandler, [self.stream_printer_event_handler], self.analysis_context, "Default")
        self.assertRaises(TypeError, JsonConverterHandler, [self.stream_printer_event_handler], self.analysis_context, b"Default")
        self.assertRaises(TypeError, JsonConverterHandler, [self.stream_printer_event_handler], self.analysis_context, 123)
        self.assertRaises(TypeError, JsonConverterHandler, [self.stream_printer_event_handler], self.analysis_context, 123.3)
        self.assertRaises(TypeError, JsonConverterHandler, [self.stream_printer_event_handler], self.analysis_context, {"id": "Default"})
        self.assertRaises(TypeError, JsonConverterHandler, [self.stream_printer_event_handler], self.analysis_context, ())
        self.assertRaises(TypeError, JsonConverterHandler, [self.stream_printer_event_handler], self.analysis_context, set())


if __name__ == '__main__':
    unittest.main()
