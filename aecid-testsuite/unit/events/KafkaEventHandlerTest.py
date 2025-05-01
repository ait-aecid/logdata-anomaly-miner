import time
from kafka import KafkaConsumer
from aminer.events.JsonConverterHandler import JsonConverterHandler
from aminer.events.KafkaEventHandler import KafkaEventHandler
from aminer.input.LogAtom import LogAtom
from aminer.parsing.ParserMatch import ParserMatch
from unit.TestBase import TestBase, DummyFixedDataModelElement, DummyMatchContext


class KafkaEventHandlerTest(TestBase):
    """Unittests for the KafkaEventHandler."""
    resource_name = b"testresource"
    output_logline = True
    topic = "test_topic"
    group = "test_group"
    persistence_id = "Default"
    consumer = None

    @classmethod
    def setUpClass(cls):
        """Start a KafkaConsumer."""
        cls.consumer = KafkaConsumer(
            cls.topic, bootstrap_servers=['localhost:9092'], enable_auto_commit=True, consumer_timeout_ms=60000,
            group_id=cls.group, value_deserializer=lambda x: x.decode(), api_version=(2, 0, 1), auto_offset_reset="earliest")

    @classmethod
    def tearDownClass(cls):
        """Shutdown the KafkaConsumer."""
        cls.consumer.close()

    def test1receive_event(self):
        """Test if events are processed correctly and that edge cases are caught in exceptions."""
        self.maxDiff = None
        match_context = DummyMatchContext(b" pid=")
        fdme = DummyFixedDataModelElement("s1", b" pid=")
        match_element = fdme.get_match_element("match", match_context)
        description = "jsonConverterHandlerDescription"
        t = time.time()
        test_detector = "Analysis.TestDetector"
        event_message = "An event happened!"
        sorted_log_lines = ["Event happened at /path/ 5 times.", "", "", "", ""]
        exp = '{\n  "AnalysisComponent": {\n    "AnalysisComponentIdentifier": 0,\n    "AnalysisComponentType": "%s",\n    ' \
              '"AnalysisComponentName": "%s",\n    "Message": "%s",\n    "PersistenceFileName": "%s",\n    "AffectedParserPaths": [\n' \
              '      "test/path/1",\n      "test/path/2"\n    ],\n    "LogResource": "testresource"\n  },\n  "LogData": {\n    ' \
              '"RawLogData": [\n      " pid="\n    ],\n    "Timestamps": [\n      %s\n    ],\n    "DetectionTimestamp": %s,\n    ' \
              '"LogLinesCount": 5,\n    "AnnotatedMatchElement": {\n      "match/s1": " pid="\n    }\n  }%s\n}\n'
        # This unittest tests the receive_event method with serialized data from the JsonConverterHandler.
        jch = JsonConverterHandler([self.stream_printer_event_handler], self.analysis_context)
        log_atom = LogAtom(fdme.data, ParserMatch(match_element), t, self)
        self.analysis_context.register_component(self, description)
        event_data = {"AnalysisComponent": {"AffectedParserPaths": ["test/path/1", "test/path/2"]}}
        jch.receive_event(test_detector, event_message, sorted_log_lines, event_data, log_atom, self)
        output = self.output_stream.getvalue()
        keh = KafkaEventHandler(self.analysis_context, self.topic, {
            "bootstrap_servers": ["localhost:9092"], "api_version": (2, 0, 1), "max_block_ms": 120000})
        self.assertTrue(keh.receive_event(test_detector, event_message, sorted_log_lines, output, log_atom, self))
        val = self.consumer.__next__().value
        detection_timestamp = None
        for line in val.split("\n"):
            if "DetectionTimestamp" in line:
                detection_timestamp = line.split(":")[1].strip(" ,")
        self.assertEqual(val, exp % (self.__class__.__name__, description, event_message, self.persistence_id, round(t, 2), detection_timestamp, ""))

        # This unittest tests the receive_event method with not serialized data.
        log_atom = LogAtom(fdme.data, ParserMatch(match_element), t, self)
        event_data = {"AnalysisComponent": {"AffectedParserPaths": ["test/path/1", "test/path/2"]}}
        keh = KafkaEventHandler(self.analysis_context, self.topic, {
            "bootstrap_servers": ["localhost:9092"], "api_version": (2, 0, 1), "max_block_ms": 120000})
        self.assertFalse(keh.receive_event(test_detector, event_message, sorted_log_lines, event_data, log_atom, self))
        self.assertRaises(StopIteration, self.consumer.__next__)

        # test output_event_handlers
        self.output_event_handlers = []
        self.assertTrue(keh.receive_event(test_detector, event_message, sorted_log_lines, output, log_atom, self))
        self.assertRaises(StopIteration, self.consumer.__next__)

        self.output_event_handlers = [keh]
        self.assertTrue(keh.receive_event(test_detector, event_message, sorted_log_lines, output, log_atom, self))
        val = self.consumer.__next__().value
        detection_timestamp = None
        for line in val.split("\n"):
            if "DetectionTimestamp" in line:
                detection_timestamp = line.split(":")[1].strip(" ,")
        self.assertEqual(val, exp % (self.__class__.__name__, description, event_message, self.persistence_id, round(t, 2), detection_timestamp, ""))

        # test suppress detector list
        self.output_event_handlers = None
        self.analysis_context.suppress_detector_list = [description]
        self.assertTrue(keh.receive_event(test_detector, event_message, sorted_log_lines, output, log_atom, self))
        self.assertRaises(StopIteration, self.consumer.__next__)

        self.output_event_handlers = [keh]
        self.analysis_context.suppress_detector_list = []
        self.assertTrue(keh.receive_event(test_detector, event_message, sorted_log_lines, output, log_atom, self))
        val = self.consumer.__next__().value
        detection_timestamp = None
        for line in val.split("\n"):
            if "DetectionTimestamp" in line:
                detection_timestamp = line.split(":")[1].strip(" ,")
        self.assertEqual(val, exp % (self.__class__.__name__, description, event_message, self.persistence_id, round(t, 2), detection_timestamp, ""))

    def test2validate_parameters(self):
        """Test all initialization parameters for the event handler. Input parameters must be validated in the class."""
        options = {"bootstrap_servers": ["localhost:9092"], "api_version": (2, 0, 1), "max_block_ms": 120000}
        KafkaEventHandler(self.analysis_context, self.topic, options)

        self.assertRaises(TypeError, KafkaEventHandler, self.analysis_context, ["default"], options)
        self.assertRaises(TypeError, KafkaEventHandler, self.analysis_context, None, options)
        self.assertRaises(TypeError, KafkaEventHandler, self.analysis_context, b"Default", options)
        self.assertRaises(TypeError, KafkaEventHandler, self.analysis_context, True, options)
        self.assertRaises(TypeError, KafkaEventHandler, self.analysis_context, 123, options)
        self.assertRaises(TypeError, KafkaEventHandler, self.analysis_context, 123.3, options)
        self.assertRaises(TypeError, KafkaEventHandler, self.analysis_context, {"id": "Default"}, options)
        self.assertRaises(TypeError, KafkaEventHandler, self.analysis_context, (), options)
        self.assertRaises(TypeError, KafkaEventHandler, self.analysis_context, set(), options)
        self.assertRaises(ValueError, KafkaEventHandler, self.analysis_context, "", options)

        self.assertRaises(TypeError, KafkaEventHandler, self.analysis_context, self.topic, ["default"])
        self.assertRaises(TypeError, KafkaEventHandler, self.analysis_context, self.topic, b"default")
        self.assertRaises(TypeError, KafkaEventHandler, self.analysis_context, self.topic, "default")
        self.assertRaises(TypeError, KafkaEventHandler, self.analysis_context, self.topic, None)
        self.assertRaises(TypeError, KafkaEventHandler, self.analysis_context, self.topic, True)
        self.assertRaises(TypeError, KafkaEventHandler, self.analysis_context, self.topic, 123)
        self.assertRaises(TypeError, KafkaEventHandler, self.analysis_context, self.topic, 123.3)
        self.assertRaises(TypeError, KafkaEventHandler, self.analysis_context, self.topic, ())
        self.assertRaises(TypeError, KafkaEventHandler, self.analysis_context, self.topic, set())
        self.assertRaises(TypeError, KafkaEventHandler, self.analysis_context, self.topic, {b"bootstrap_servers": ["localhost:9092"]})
        KafkaEventHandler(self.analysis_context, self.topic, {})
