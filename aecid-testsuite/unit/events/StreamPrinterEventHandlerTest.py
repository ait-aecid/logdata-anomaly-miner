import unittest
from aminer.parsing.MatchContext import MatchContext
from aminer.parsing.FixedDataModelElement import FixedDataModelElement
from time import time
from aminer.parsing.ParserMatch import ParserMatch
from aminer.input.LogAtom import LogAtom
from unit.TestBase import TestBase
from datetime import datetime


class StreamPrinterEventHandlerTest(TestBase):
    __expectedString = '%s New value for pathes %s: %s\n%s: "%s" (%d lines)\n%s\n'

    pid = b' pid='
    test = 'Test.%s'
    match_s1 = 'match/s1'
    match_s2 = 'match/s2'
    new_val = 'New value for pathes %s, %s: %s'

    def test1log_multiple_lines_event(self):
        """In this test case the EventHandler receives multiple lines from the test class."""
        description = "Test1StreamPrinterEventHandler"
        match_context = MatchContext(self.pid)
        fixed_dme = FixedDataModelElement('s1', self.pid)
        match_element = fixed_dme.get_match_element("match", match_context)

        match_context = MatchContext(self.pid)
        fixed_dme2 = FixedDataModelElement('s2', self.pid)
        match_element2 = fixed_dme2.get_match_element("match", match_context)
        self.analysis_context.register_component(self, description)
        t = time()
        log_atom = LogAtom(fixed_dme.fixed_data, ParserMatch(match_element), t, self)

        self.stream_printer_event_handler.receive_event(self.test % self.__class__.__name__,
            self.new_val % (self.match_s1, self.match_s2, repr(match_element.match_object)), [log_atom.raw_data, log_atom.raw_data], None,
            log_atom, self)

        self.assertEqual(self.output_stream.getvalue(), self.__expectedString % (
            datetime.fromtimestamp(t).strftime("%Y-%m-%d %H:%M:%S"), match_element.get_path() + ", " + match_element2.get_path(),
            match_element.get_match_object(), self.__class__.__name__, description, 2,
            "  " + match_element.get_match_string().decode() + "\n  " + match_element2.get_match_string().decode() + "\n"))

    def test2log_no_line_event(self):
        """In this test case the EventHandler receives no lines from the test class."""
        description = "Test2StreamPrinterEventHandler"
        match_context = MatchContext(self.pid)
        fixed_dme = FixedDataModelElement('s1', self.pid)
        match_element = fixed_dme.get_match_element("match", match_context)

        match_context = MatchContext(self.pid)
        fixed_dme2 = FixedDataModelElement('s2', self.pid)
        match_element2 = fixed_dme2.get_match_element("match", match_context)
        self.analysis_context.register_component(self, description)
        t = time()
        log_atom = LogAtom(fixed_dme.fixed_data, ParserMatch(match_element), t, self)

        self.stream_printer_event_handler.receive_event(
            self.test % self.__class__.__name__, self.new_val % (self.match_s1, self.match_s2, repr(match_element.match_object)), [],
            None, log_atom, self)

        self.assertEqual(self.output_stream.getvalue(), self.__expectedString % (
            datetime.fromtimestamp(t).strftime("%Y-%m-%d %H:%M:%S"), match_element.get_path() + ", " + match_element2.get_path(),
            match_element.get_match_object(), self.__class__.__name__, description, 0, ""))

    def test3event_data_not_log_atom(self):
        """In this test case the EventHandler receives no logAtom from the test class and the method should raise an exception."""
        description = "Test3StreamPrinterEventHandler"
        match_context = MatchContext(self.pid)
        fixed_dme = FixedDataModelElement('s1', self.pid)
        match_element = fixed_dme.get_match_element("match", match_context)
        self.analysis_context.register_component(self, description)
        t = time()
        log_atom = LogAtom(fixed_dme.fixed_data, ParserMatch(match_element), t, self)

        self.assertRaises(Exception, self.stream_printer_event_handler.receive_event, self.test % self.__class__.__name__,
                          self.new_val % (self.match_s1, self.match_s2, repr(match_element.match_object)),
                          [log_atom.raw_data, log_atom.raw_data], log_atom.get_parser_match(), self)


if __name__ == "__main__":
    unittest.main()
