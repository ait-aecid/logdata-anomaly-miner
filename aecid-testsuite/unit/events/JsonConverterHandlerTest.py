import time
import unittest
from datetime import datetime
from aminer.events.JsonConverterHandler import JsonConverterHandler
from aminer.input.LogAtom import LogAtom
from aminer.parsing.MatchContext import MatchContext
from aminer.parsing.FixedDataModelElement import FixedDataModelElement
from aminer.parsing.ParserMatch import ParserMatch
from unit.TestBase import TestBase


class JsonConverterHandlerTest(TestBase):
    """Unittests for the JsonConverterHandler."""

    output_log_line = True
    match_context = MatchContext(b' pid=')
    fixed_dme = FixedDataModelElement('s1', b' pid=')
    match_element = fixed_dme.get_match_element("match", match_context)
    t = time.time()

    test_detector = 'Analysis.TestDetector'
    event_message = 'An event happened!'
    sorted_log_lines = ['Event happend at /path/ 5 times.', '', '', '', '']
    persistence_id = 'Default'
    description = 'jsonConverterHandlerDescription'
    expected_string = '%s %s\n%s: "%s" (5 lines)\n  {\n  "AnalysisComponent": {\n    "AnalysisComponentIdentifier": 0,\n' \
                      '    "AnalysisComponentType": "%s",\n    "AnalysisComponentName": "%s",\n    "Message": "%s",\n' \
                      '    "PersistenceFileName": "%s",\n    "AffectedParserPaths": [\n      "test/path/1",\n' \
                      '      "test/path/2"\n    ]\n  },\n  "LogData": {\n    "RawLogData": [\n      " pid="\n    ],\n    ' \
                      '"Timestamps": [\n      %s\n    ],\n    "LogLinesCount": 5,\n' \
                      '    "AnnotatedMatchElement": "match/s1: b\' pid=\'"\n  }%s\n}\n\n'

    def test1receive_expected_event(self):
        """In this test case a normal Event happens and the json output should be sent to a StreamPrinterEventHandler."""
        json_converter_handler = JsonConverterHandler([self.stream_printer_event_handler], self.analysis_context)
        log_atom = LogAtom(self.fixed_dme.fixed_data, ParserMatch(self.match_element), self.t, self)
        self.analysis_context.register_component(self, self.description)
        event_data = {'AnalysisComponent': {'AffectedParserPaths': ['test/path/1', 'test/path/2']}}
        json_converter_handler.receive_event(self.test_detector, self.event_message, self.sorted_log_lines, event_data, log_atom, self)
        self.assertEqual(
            self.output_stream.getvalue(), self.expected_string % (
                datetime.fromtimestamp(self.t).strftime("%Y-%m-%d %H:%M:%S"), self.event_message, self.__class__.__name__,
                self.description, self.__class__.__name__, self.description, self.event_message, self.persistence_id, round(self.t, 2), ""))

    def test2receive_event_with_same_event_data_attributes(self):
        """In this test case an attribute of AnalysisComponent is overwritten and an JsonError attribute is expected."""
        json_converter_handler = JsonConverterHandler([self.stream_printer_event_handler], self.analysis_context)
        log_atom = LogAtom(self.fixed_dme.fixed_data, ParserMatch(self.match_element), self.t, self)
        self.analysis_context.register_component(self, self.description)
        event_data = {'AnalysisComponent': {'AffectedParserPaths': ['test/path/1', 'test/path/2'],
                      'Message': 'An other event happened too!'}}
        json_converter_handler.receive_event(self.test_detector, self.event_message, self.sorted_log_lines,
                                             event_data, log_atom, self)
        self.assertEqual(
            self.output_stream.getvalue(), self.expected_string % (
                datetime.fromtimestamp(self.t).strftime("%Y-%m-%d %H:%M:%S"), self.event_message, self.__class__.__name__,
                self.description, self.__class__.__name__, self.description, self.event_message, self.persistence_id,
                round(float("%.2f" % self.t), 2),
                ',\n  "JsonError": "AnalysisComponent attribute \'Message\' is already in use and can not be overwritten!\\n"'))


if __name__ == '__main__':
    unittest.main()
