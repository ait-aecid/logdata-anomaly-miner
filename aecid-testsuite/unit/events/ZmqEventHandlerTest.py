import time
import zmq
from aminer.events.JsonConverterHandler import JsonConverterHandler
from aminer.events.ZmqEventHandler import ZmqEventHandler
from aminer.input.LogAtom import LogAtom
from aminer.parsing.ParserMatch import ParserMatch
from unit.TestBase import TestBase, DummyFixedDataModelElement, DummyMatchContext


class ZmqEventHandlerTest(TestBase):
    """Unittests for the ZmqEventHandler."""

    resource_name = b"testresource"
    pub_url = "tcp://*:5555"
    sub_url = "tcp://localhost:5555"
    topic = "test_topic"
    description = "jsonConverterHandlerDescription"
    persistence_id = "Default"
    test_detector = "Analysis.TestDetector"
    event_message = "An event happened!"
    sorted_log_lines = ["Event happend at /path/ 5 times.", "", "", "", ""]
    expected_string = '{\n  "AnalysisComponent": {\n    "AnalysisComponentIdentifier": 0,\n' \
                      '    "AnalysisComponentType": "%s",\n    "AnalysisComponentName": "%s",\n    "Message": "%s",\n' \
                      '    "PersistenceFileName": "%s",\n    "AffectedParserPaths": [\n      "test/path/1",\n' \
                      '      "test/path/2"\n    ],\n    "LogResource": "testresource"\n  },\n  "LogData": {\n    "RawLogData": [\n      " pid="\n    ],\n    ' \
                      '"Timestamps": [\n      %s\n    ],\n    "DetectionTimestamp": %s,\n    "LogLinesCount": 5\n  }%s\n}\n'

    match_context1 = DummyMatchContext(b" pid=")
    fdme1 = DummyFixedDataModelElement("s1", b" pid=")
    match_element1 = fdme1.get_match_element("", match_context1)

    @classmethod
    def setUpClass(cls):
        """Start a ZmqConsumer."""
        cls.context = zmq.Context()
        cls.consumer = cls.context.socket(zmq.SUB)
        cls.consumer.connect(cls.sub_url)
        cls.consumer.setsockopt_string(zmq.SUBSCRIBE, cls.topic)

    @classmethod
    def tearDownClass(cls):
        """Shutdown the ZmqConsumer."""
        cls.consumer.close()
        cls.context.destroy()

    def test1receive_event(self):
        """Test if events are processed correctly and that edge cases are caught in exceptions."""
        self.maxDiff = None
        json_converter_handler = JsonConverterHandler([self.stream_printer_event_handler], self.analysis_context)
        t = round(time.time(), 3)
        log_atom = LogAtom(self.fdme1.data, ParserMatch(self.match_element1), t, self)
        self.analysis_context.register_component(self, self.description)
        event_data = {'AnalysisComponent': {'AffectedParserPaths': ['test/path/1', 'test/path/2']}}
        json_converter_handler.receive_event(self.test_detector, self.event_message, self.sorted_log_lines, event_data, log_atom, self)
        output = self.output_stream.getvalue()
        zmq_event_handler = ZmqEventHandler(self.analysis_context, self.topic, self.pub_url)
        self.assertTrue(zmq_event_handler.receive_event(self.test_detector, self.event_message, self.sorted_log_lines, output, log_atom, self))
        topic = self.consumer.recv_string()
        self.assertEqual(self.topic, topic)
        val = self.consumer.recv_string()
        detection_timestamp = None
        for line in val.split('\n'):
            if "DetectionTimestamp" in line:
                detection_timestamp = line.split(':')[1].strip(' ,')
        self.assertEqual(val, self.expected_string % (
            self.__class__.__name__, self.description, self.event_message, self.persistence_id, round(t, 2), detection_timestamp, ""))


        # test event source

        # test output event handlers

        # test suppress detector list

        # test etc

        # ZmqEventHandler implementation is flawed, because the subscriber can not subscribe before the socket is bound. Messages sent before
        # the subscriber is connected are lost. It is practically not possible for the subscriber to connect before the first message is sent and therefore
        # the first message is always lost

        zmq_event_handler.producer.close()
        zmq_event_handler.context.destroy()

    def test2validate_parameters(self):
        """Test all initialization parameters for the event handler. Input parameters must be validated in the class."""
        pass

    # resource_name = b"testresource"
    # output_logline = True
    # kafka_group = 'test_group'
    # consumer = None
    # match_context = MatchContext(b' pid=')
    # fixed_dme = FixedDataModelElement('s1', b' pid=')
    # other_data = 4
    # match_element = fixed_dme.get_match_element("match", match_context)
    # description = 'jsonConverterHandlerDescription'
    # t = time.time()
    # persistence_id = 'Default'
    # test_detector = 'Analysis.TestDetector'
    # event_message = 'An event happened!'
    # sorted_log_lines = ['Event happend at /path/ 5 times.', '', '', '', '']
    # expected_string = '{\n  "AnalysisComponent": {\n    "AnalysisComponentIdentifier": 0,\n' \
    #                   '    "AnalysisComponentType": "%s",\n    "AnalysisComponentName": "%s",\n    "Message": "%s",\n' \
    #                   '    "PersistenceFileName": "%s",\n    "AffectedParserPaths": [\n      "test/path/1",\n' \
    #                   '      "test/path/2"\n    ],\n    "LogResource": "testresource"\n  },\n  "LogData": {\n    "RawLogData": [\n      " pid="\n    ],\n    ' \
    #                   '"Timestamps": [\n      %s\n    ],\n    "DetectionTimestamp": %s,\n    "LogLinesCount": 5,\n' \
    #                   '    "AnnotatedMatchElement": {\n      "match/s1": " pid="\n    }\n  }%s\n}\n'
    #
    # def test1receive_serialized_data(self):
    #     """This unittest tests the receive_event method with serialized data from the JsonConverterHandler."""
    #     json_converter_handler = JsonConverterHandler([self.stream_printer_event_handler], self.analysis_context)
    #     log_atom = LogAtom(self.fixed_dme.fixed_data, ParserMatch(self.match_element), self.t, self)
    #     self.analysis_context.register_component(self, self.description)
    #     event_data = {'AnalysisComponent': {'AffectedParserPaths': ['test/path/1', 'test/path/2']}}
    #     json_converter_handler.receive_event(self.test_detector, self.event_message, self.sorted_log_lines, event_data, log_atom, self)
    #     output = self.output_stream.getvalue()
    #     kafka_event_handler = KafkaEventHandler(self.analysis_context, self.kafka_topic, {
    #         'bootstrap_servers': ['localhost:9092'], 'api_version': (2, 0, 1), 'max_block_ms': 120000})
    #     self.assertTrue(kafka_event_handler.receive_event(self.test_detector, self.event_message, self.sorted_log_lines, output, log_atom,
    #                                                       self))
    #     val = self.consumer.__next__().value
    #     detection_timestamp = None
    #     for line in val.split('\n'):
    #         if "DetectionTimestamp" in line:
    #             detection_timestamp = line.split(':')[1].strip(' ,')
    #     self.assertEqual(val, self.expected_string % (
    #         self.__class__.__name__, self.description, self.event_message, self.persistence_id, round(self.t, 2), detection_timestamp,
    #         ""))
    #
    # def test2receive_non_serialized_data(self):
    #     """This unittest tests the receive_event method with not serialized data."""
    #     log_atom = LogAtom(self.fixed_dme.fixed_data, ParserMatch(self.match_element), self.t, self)
    #     self.analysis_context.register_component(self, self.description)
    #     event_data = {'AnalysisComponent': {'AffectedParserPaths': ['test/path/1', 'test/path/2']}}
    #     kafka_event_handler = KafkaEventHandler(self.analysis_context, self.kafka_topic, {
    #         'bootstrap_servers': ['localhost:9092'], 'api_version': (2, 0, 1), 'max_block_ms': 120000})
    #     self.assertFalse(kafka_event_handler.receive_event(self.test_detector, self.event_message, self.sorted_log_lines, event_data,
    #                                                        log_atom, self))
    #     self.assertRaises(StopIteration, self.consumer.__next__)


if __name__ == "__main__":
    unittest.main()
