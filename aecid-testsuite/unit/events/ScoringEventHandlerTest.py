import time
from aminer.events.ScoringEventHandler import ScoringEventHandler
from aminer.analysis.SlidingEventFrequencyDetector import SlidingEventFrequencyDetector
from aminer.events.JsonConverterHandler import JsonConverterHandler
from aminer.input.LogAtom import LogAtom
from aminer.parsing.ParserMatch import ParserMatch
from aminer.parsing.MatchElement import MatchElement
from datetime import datetime
from unit.TestBase import TestBase, DummyFixedDataModelElement, DummyMatchContext


class ScoringEventHandlerTest(TestBase):
    """Unittests for the ScoringEventHandler."""

    resource_name = b"testresource"
    pub_url = "tcp://*:5555"
    sub_url = "tcp://localhost:5555"
    topic = "test_topic"
    description = "jsonConverterHandlerDescription"
    persistence_id = "Default"
    test_detector = "Analysis.TestDetector"
    sorted_log_lines = ["Event happend at /path/ 5 times.", "", "", "", ""]
    expected_string = '{\n  "AnalysisComponent": {\n    "AnalysisComponentIdentifier": 1,\n    "AnalysisComponentType": "%s",\n    ' \
                      '"AnalysisComponentName": "%s",\n    "Message": "%s",\n    "PersistenceFileName": "Default",\n    "TrainingMode": true,\n' \
                      '    "AffectedLogAtomPaths": [],\n    "AffectedLogAtomValues": [\n      "/value"\n    ],\n    ' \
                      '"LogResource": "SlidingEventFrequencyDetector"\n  },\n  "FrequencyData": {\n' \
                      '    "ExpectedLogAtomValuesFrequencyRange": [\n      0,\n      2\n    ],\n    "LogAtomValuesFrequency": %d,\n    ' \
                      '"WindowSize": 10%s\n  },\n  "LogData": {\n    "RawLogData": [\n      "%s"\n    ],\n    ' \
                      '"Timestamps": [\n      %s\n    ],\n    "DetectionTimestamp": %s,\n    "LogLinesCount": 1\n  }%s\n}\n'

    match_context1 = DummyMatchContext(b" pid=")
    fdme1 = DummyFixedDataModelElement("s1", b" pid=")
    match_element1 = fdme1.get_match_element("", match_context1)

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def test1receive_event(self):
        """Test if events are processed correctly."""
        self.maxDiff = None
        t = round(time.time(), 3)
        log_atom = LogAtom(self.fdme1.data, ParserMatch(self.match_element1), t, self)
        self.analysis_context.register_component(self, self.description)
        event_data = {'AnalysisComponent': {'AffectedParserPaths': ['test/path/1', 'test/path/2']}}
        json_converter_handler = JsonConverterHandler([self.stream_printer_event_handler], self.analysis_context)
        scoring_event_handler = ScoringEventHandler([json_converter_handler], self.analysis_context)
        scoring_event_handler.receive_event(self.test_detector, "Frequency exceeds range for the first time", self.sorted_log_lines, event_data, log_atom, self)
        self.reset_output_stream()

        t = time.time()
        sefd = SlidingEventFrequencyDetector(aminer_config=self.aminer_config, anomaly_event_handlers=[scoring_event_handler],
                                             window_size=10, set_upper_limit=2, learn_mode=True, output_logline=False, scoring_path_list=["/value"])
        sefd_name = "SlidingEventFrequencyDetector"
        self.analysis_context.register_component(sefd, sefd_name)
        sefd.resource_name = b"SlidingEventFrequencyDetector"

        # Prepare log atoms that represent different amounts of values a, b over time
        # Four time windows are used. The first time window is used for initialization. The
        # second time window represents normal behavior, i.e., the frequencies do not change
        # too much and no anomalies should be generated. The third window contains changes
        # of value frequencies and thus anomalies should be generated. The fourth time window
        # only has the purpose of marking the end of the third time window.
        # The following log atoms are created:
        #  window 1:
        #   value a: 2 times
        #   value b: 1 time
        #  window 2:
        #   value a: 3 times
        #   value b: 1 time
        #  window 3:
        #   value a: 0 times
        #   value b: 2 times
        #  window 4:
        #   value a: 1 time
        # Start of window 1:
        log_atom1 = LogAtom(b"a", ParserMatch(MatchElement("/value", b"a", b"a", None)), t + 1, sefd)
        log_atom2 = LogAtom(b"b", ParserMatch(MatchElement("/value", b"b", b"b", None)), t + 3, sefd)
        log_atom3 = LogAtom(b"a", ParserMatch(MatchElement("/value", b"a", b"a", None)), t + 7, sefd)

        # Start of window 2:
        log_atom4 = LogAtom(b"a", ParserMatch(MatchElement("/value", b"a", b"a", None)), t + 13, sefd)
        log_atom5 = LogAtom(b"b", ParserMatch(MatchElement("/value", b"b", b"b", None)), t + 17, sefd)
        log_atom6 = LogAtom(b"a", ParserMatch(MatchElement("/value", b"a", b"a", None)), t + 18, sefd)
        log_atom7 = LogAtom(b"a", ParserMatch(MatchElement("/value", b"a", b"a", None)), t + 19, sefd)

        # Start of window 3:
        log_atom8 = LogAtom(b"b", ParserMatch(MatchElement("/value", b"b", b"b", None)), t + 25, sefd)
        log_atom9 = LogAtom(b"b", ParserMatch(MatchElement("/value", b"b", b"b", None)), t + 25, sefd)

        # Start of window 4:
        log_atom10 = LogAtom(b"a", ParserMatch(MatchElement("/value", b"a", b"a", None)), t + 35, sefd)

        sefd.receive_atom(log_atom1)
        self.assertEqual(self.output_stream.getvalue(), "")
        self.assertEqual(list(sefd.counts[("/value",)]), [t + 1])

        sefd.receive_atom(log_atom2)
        self.assertEqual(self.output_stream.getvalue(), "")
        self.assertEqual(list(sefd.counts[("/value",)]), [t + 1, t + 3])

        sefd.receive_atom(log_atom3)
        detection_timestamp = None
        for line in self.output_stream.getvalue().split('\n'):
            if "DetectionTimestamp" in line:
                detection_timestamp = line.split(':')[1].strip(' ,')
                break
        self.assertEqual(self.output_stream.getvalue(),
                         self.expected_string % (sefd_name, sefd_name, "Frequency exceeds range for the first time", 3, "", "a", round(t + 7, 2), detection_timestamp, ""))
        self.reset_output_stream()
        self.assertEqual(list(sefd.counts[("/value",)]), [t + 1, t + 3, t + 7])

        sefd.receive_atom(log_atom4)
        self.assertEqual(self.output_stream.getvalue(), "")
        self.assertEqual(list(sefd.counts[("/value",)]), [t + 3, t + 7, t + 13])

        sefd.receive_atom(log_atom5)
        self.assertEqual(self.output_stream.getvalue(), "")
        self.assertEqual(list(sefd.counts[("/value",)]), [t + 7, t + 13, t + 17])

        sefd.receive_atom(log_atom6)
        self.assertEqual(self.output_stream.getvalue(), "")
        self.assertEqual(list(sefd.counts[("/value",)]), [t + 13, t + 17, t + 18])

        sefd.receive_atom(log_atom7)
        self.assertEqual(self.output_stream.getvalue(), "")
        self.assertEqual(list(sefd.counts[("/value",)]), [t + 13, t + 17, t + 18, t + 19])

        sefd.receive_atom(log_atom8)
        self.assertEqual(self.output_stream.getvalue(), "")
        self.assertEqual(list(sefd.counts[("/value",)]), [t + 17, t + 18, t + 19, t + 25])

        sefd.receive_atom(log_atom9)
        self.assertEqual(self.output_stream.getvalue(), "")
        self.assertEqual(list(sefd.counts[("/value",)]), [t + 17, t + 18, t + 19, t + 25, t + 25])

        sefd.receive_atom(log_atom10)
        for line in self.output_stream.getvalue().split('\n'):
            if "DetectionTimestamp" in line:
                detection_timestamp = line.split(':')[1].strip(' ,')
                break
        scoring_result = ',\n    "Confidence": 0.6,\n    "Local_maximum_timestamp": %s,\n    "IdValues": [\n      "b",\n      "a",\n      ' \
                         '"a",\n      "b",\n      "b"\n    ],\n    "Scoring": {\n      "confidence_absolut": 2.5,\n      ' \
                         '"confidence_mean": 0.5\n    }' % str(round(t + 25, 2))
        self.assertEqual(self.output_stream.getvalue(),
                         self.expected_string % (sefd_name, sefd_name, "Frequency anomaly detected", 5, scoring_result, "b", round(t + 25, 2), detection_timestamp, ""))
        self.reset_output_stream()
        self.assertEqual(list(sefd.counts[("/value",)]), [t + 25, t + 25, t + 35])

    def test2validate_parameters(self):
        """Test all initialization parameters for the event handler. Input parameters must be validated in the class."""
        self.assertRaises(TypeError, ScoringEventHandler, "Default", self.analysis_context)
        self.assertRaises(TypeError, ScoringEventHandler, b"Default", self.analysis_context)
        self.assertRaises(TypeError, ScoringEventHandler, True, self.analysis_context)
        self.assertRaises(TypeError, ScoringEventHandler, 123, self.analysis_context)
        self.assertRaises(TypeError, ScoringEventHandler, 123.3, self.analysis_context)
        self.assertRaises(TypeError, ScoringEventHandler, {"id": "Default"}, self.analysis_context)
        self.assertRaises(TypeError, ScoringEventHandler, ["string"], self.analysis_context)
        self.assertRaises(TypeError, ScoringEventHandler, ["string", self.stream_printer_event_handler], self.analysis_context)
        self.assertRaises(ValueError, ScoringEventHandler, set(), self.analysis_context)
        self.assertRaises(ValueError, ScoringEventHandler, (), self.analysis_context)
        self.assertRaises(ValueError, ScoringEventHandler, None, self.analysis_context)
        self.assertRaises(ValueError, ScoringEventHandler, [], self.analysis_context)

        self.assertRaises(TypeError, ScoringEventHandler, [self.stream_printer_event_handler], "Default")
        self.assertRaises(TypeError, ScoringEventHandler, [self.stream_printer_event_handler], b"Default")
        self.assertRaises(TypeError, ScoringEventHandler, [self.stream_printer_event_handler], True)
        self.assertRaises(TypeError, ScoringEventHandler, [self.stream_printer_event_handler], 123)
        self.assertRaises(TypeError, ScoringEventHandler, [self.stream_printer_event_handler], 123.3)
        self.assertRaises(TypeError, ScoringEventHandler, [self.stream_printer_event_handler], {"id": "Default"})
        self.assertRaises(TypeError, ScoringEventHandler, [self.stream_printer_event_handler], ["string"])
        self.assertRaises(TypeError, ScoringEventHandler, [self.stream_printer_event_handler], set())
        self.assertRaises(TypeError, ScoringEventHandler, [self.stream_printer_event_handler], ())
        self.assertRaises(TypeError, ScoringEventHandler, [self.stream_printer_event_handler], None)
        self.assertRaises(TypeError, ScoringEventHandler, [self.stream_printer_event_handler], [])

        self.assertRaises(TypeError, ScoringEventHandler, [self.stream_printer_event_handler], self.analysis_context, weights="Default")
        self.assertRaises(TypeError, ScoringEventHandler, [self.stream_printer_event_handler], self.analysis_context, weights=b"Default")
        self.assertRaises(TypeError, ScoringEventHandler, [self.stream_printer_event_handler], self.analysis_context, weights=True)
        self.assertRaises(TypeError, ScoringEventHandler, [self.stream_printer_event_handler], self.analysis_context, weights=123)
        self.assertRaises(TypeError, ScoringEventHandler, [self.stream_printer_event_handler], self.analysis_context, weights=123.3)
        self.assertRaises(TypeError, ScoringEventHandler, [self.stream_printer_event_handler], self.analysis_context, weights={"id": "Default"})
        self.assertRaises(TypeError, ScoringEventHandler, [self.stream_printer_event_handler], self.analysis_context, weights=["string"])
        self.assertRaises(TypeError, ScoringEventHandler, [self.stream_printer_event_handler], self.analysis_context, weights=set())
        self.assertRaises(TypeError, ScoringEventHandler, [self.stream_printer_event_handler], self.analysis_context, weights=())
        self.assertRaises(TypeError, ScoringEventHandler, [self.stream_printer_event_handler], self.analysis_context, weights=[])

        self.assertRaises(TypeError, ScoringEventHandler, [self.stream_printer_event_handler], self.analysis_context, auto_weights="Default")
        self.assertRaises(TypeError, ScoringEventHandler, [self.stream_printer_event_handler], self.analysis_context, auto_weights=b"Default")
        self.assertRaises(TypeError, ScoringEventHandler, [self.stream_printer_event_handler], self.analysis_context, auto_weights=123)
        self.assertRaises(TypeError, ScoringEventHandler, [self.stream_printer_event_handler], self.analysis_context, auto_weights=123.3)
        self.assertRaises(TypeError, ScoringEventHandler, [self.stream_printer_event_handler], self.analysis_context, auto_weights={"id": "Default"})
        self.assertRaises(TypeError, ScoringEventHandler, [self.stream_printer_event_handler], self.analysis_context, auto_weights=["string"])
        self.assertRaises(TypeError, ScoringEventHandler, [self.stream_printer_event_handler], self.analysis_context, auto_weights=set())
        self.assertRaises(TypeError, ScoringEventHandler, [self.stream_printer_event_handler], self.analysis_context, auto_weights=())
        self.assertRaises(TypeError, ScoringEventHandler, [self.stream_printer_event_handler], self.analysis_context, auto_weights=[])

        self.assertRaises(TypeError, ScoringEventHandler, [self.stream_printer_event_handler], self.analysis_context, auto_weights_history_length="Default")
        self.assertRaises(TypeError, ScoringEventHandler, [self.stream_printer_event_handler], self.analysis_context, auto_weights_history_length=b"Default")
        self.assertRaises(TypeError, ScoringEventHandler, [self.stream_printer_event_handler], self.analysis_context, auto_weights_history_length=True)
        self.assertRaises(TypeError, ScoringEventHandler, [self.stream_printer_event_handler], self.analysis_context, auto_weights_history_length=123.3)
        self.assertRaises(TypeError, ScoringEventHandler, [self.stream_printer_event_handler], self.analysis_context, auto_weights_history_length={"id": "Default"})
        self.assertRaises(TypeError, ScoringEventHandler, [self.stream_printer_event_handler], self.analysis_context, auto_weights_history_length=["string"])
        self.assertRaises(TypeError, ScoringEventHandler, [self.stream_printer_event_handler], self.analysis_context, auto_weights_history_length=set())
        self.assertRaises(TypeError, ScoringEventHandler, [self.stream_printer_event_handler], self.analysis_context, auto_weights_history_length=())
        self.assertRaises(TypeError, ScoringEventHandler, [self.stream_printer_event_handler], self.analysis_context, auto_weights_history_length=[])
        self.assertRaises(ValueError, ScoringEventHandler, [self.stream_printer_event_handler], self.analysis_context, auto_weights_history_length=0)
        ScoringEventHandler([self.stream_printer_event_handler], self.analysis_context, weights = {"value": 0.5}, auto_weights=True, auto_weights_history_length=101)


if __name__ == "__main__":
    unittest.main()
