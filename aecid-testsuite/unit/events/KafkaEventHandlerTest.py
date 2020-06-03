import time
from datetime import datetime
from kafka import KafkaConsumer
from aminer.events.JsonConverterHandler import JsonConverterHandler
from aminer.events.KafkaEventHandler import KafkaEventHandler
from aminer.input import LogAtom
from aminer.parsing import MatchContext, FixedDataModelElement, ParserMatch
from unit.TestBase import TestBase


class KafkaEventHandlerTest(TestBase):
    output_log_line = True
    kafka_topic = 'test_topic'
    kafka_group = 'test_group'
    consumer = None
    match_context = MatchContext(b' pid=')
    fixed_dme = FixedDataModelElement('s1', b' pid=')
    other_data = 4
    match_element = fixed_dme.get_match_element("match", match_context)
    description = 'jsonConverterHandlerDescription'
    t = time.time()
    persistence_id = 'Default'
    test_detector = 'Analysis.TestDetector'
    event_message = 'An event happened!'
    sorted_log_lines = ['Event happend at /path/ 5 times.', '', '', '', '']
    expected_string = '%s %s\n%s: "%s" (5 lines)\n  {\n  "AnalysisComponent": {\n    "AnalysisComponentIdentifier": 0,\n' \
                      '    "AnalysisComponentType": "%s",\n    "AnalysisComponentName": "%s",\n    "Message": "%s",\n' \
                      '    "PersistenceFileName": "%s",\n    "AffectedParserPaths": [\n      "test/path/1",\n' \
                      '      "test/path/2"\n    ]\n  },\n  "LogData": {\n    "RawLogData": [\n      " pid="\n    ],\n    ' \
                      '"Timestamps": [\n      %s\n    ],\n    "LogLinesCount": 5,\n' \
                      '    "AnnotatedMatchElement": "match/s1: b\' pid=\'"\n  }%s\n}\n\n'

    @classmethod
    def setUpClass(cls):
        cls.consumer = KafkaConsumer(
            cls.kafka_topic, bootstrap_servers=['localhost:9092'], enable_auto_commit=True, consumer_timeout_ms=10000,
            group_id=cls.kafka_group, value_deserializer=lambda x: x.decode(), api_version=(2, 0, 1), auto_offset_reset='earliest')

    @classmethod
    def tearDownClass(cls):
        cls.consumer.close()

    def test1receive_serialized_data(self):
        """This unittest tests the receive_event method with serialized data from the JsonConverterHandler."""
        json_converter_handler = JsonConverterHandler([self.stream_printer_event_handler], self.analysis_context)
        log_atom = LogAtom(self.fixed_dme.fixed_data, ParserMatch(self.match_element), self.t, self)
        self.analysis_context.register_component(self, self.description)
        event_data = {'AnalysisComponent': {'AffectedParserPaths': ['test/path/1', 'test/path/2']}}
        json_converter_handler.receive_event(self.test_detector, self.event_message, self.sorted_log_lines, event_data, log_atom, self)
        output = self.output_stream.getvalue()
        kafka_event_handler = KafkaEventHandler(
            self.analysis_context, self.kafka_topic, {'bootstrap_servers': ['localhost:9092'], 'api_version': (2, 0, 1)})
        self.assertTrue(kafka_event_handler.receive_event(self.test_detector, self.event_message, self.sorted_log_lines, output, log_atom,
                                                          self))

        self.assertEqual(self.consumer.__next__().value, self.expected_string % (
            datetime.fromtimestamp(self.t).strftime("%Y-%m-%d %H:%M:%S"), self.event_message, self.__class__.__name__, self.description,
            self.__class__.__name__, self.description, self.event_message, self.persistence_id, round(self.t, 2), ""))

    def test2receive_non_serialized_data(self):
        """This unittest tests the receive_event method with not serialized data"""
        log_atom = LogAtom(self.fixed_dme.fixed_data, ParserMatch(self.match_element), self.t, self)
        self.analysis_context.register_component(self, self.description)
        event_data = {'AnalysisComponent': {'AffectedParserPaths': ['test/path/1', 'test/path/2']}}
        kafka_event_handler = KafkaEventHandler(
            self.analysis_context, self.kafka_topic, {'bootstrap_servers': ['localhost:9092'], 'api_version': (2, 0, 1)})
        self.assertFalse(kafka_event_handler.receive_event(self.test_detector, self.event_message, self.sorted_log_lines, event_data,
                         log_atom, self))
        self.assertRaises(StopIteration, self.consumer.__next__)
