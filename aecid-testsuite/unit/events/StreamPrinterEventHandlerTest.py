import unittest
import sys
import io
from time import time
from aminer.events.StreamPrinterEventHandler import StreamPrinterEventHandler
from aminer.parsing.ParserMatch import ParserMatch
from aminer.input.LogAtom import LogAtom
from unit.TestBase import TestBase, DummyFixedDataModelElement, DummyMatchContext
from datetime import datetime


class StreamPrinterEventHandlerTest(TestBase):
    """Unittests for the StreamPrinterEventHandler."""

    def test1receive_event(self):
        """Test if events are processed correctly and that edge cases are caught in exceptions."""
        # In this test case the EventHandler receives multiple lines from the test class.
        description = "Test1StreamPrinterEventHandler"
        exp = '%s New value for paths %s: %s\n%s: "%s" (%d lines)\n%s\n'
        pid = b" pid="
        test = "Test.%s"
        match_s1 = "match/s1"
        match_s2 = "match/s2"
        match_context = DummyMatchContext(pid)
        fdme = DummyFixedDataModelElement("s1", pid)
        match_element = fdme.get_match_element("match", match_context)

        self.analysis_context.register_component(self, description)
        t = time()
        log_atom = LogAtom(fdme.data, ParserMatch(match_element), t, self)

        new_val = "New value for paths %s, %s: %s" % (match_s1, match_s2, repr(match_element.match_object))
        self.stream_printer_event_handler.receive_event(test % self.__class__.__name__, new_val, [log_atom.raw_data, log_atom.raw_data], None, log_atom, self)

        dt = datetime.fromtimestamp(t).strftime("%Y-%m-%d %H:%M:%S")
        self.assertEqual(self.output_stream.getvalue(), exp % (dt, match_s1 + ", " + match_s2, "b' pid='", self.__class__.__name__, description, 2, "   pid=\n   pid=\n"))
        self.reset_output_stream()

        #In this test case the EventHandler receives no lines from the test class.
        self.stream_printer_event_handler.receive_event(test % self.__class__.__name__, new_val, [], None, log_atom, self)

        self.assertEqual(self.output_stream.getvalue(), exp % (dt, match_s1 + ", " + match_s2, "b' pid='", self.__class__.__name__, description, 0, ""))
        self.reset_output_stream()

        #In this test case the EventHandler receives no logAtom from the test class and the method should raise an exception.
        self.assertRaises(Exception, self.stream_printer_event_handler.receive_event, test % self.__class__.__name__,
            new_val, [log_atom.raw_data, log_atom.raw_data], log_atom.get_parser_match(), self)

        # test output_event_handlers
        self.output_event_handlers = []
        self.assertTrue(self.stream_printer_event_handler.receive_event(test % self.__class__.__name__, new_val, [log_atom.raw_data, log_atom.raw_data], None, log_atom, self))
        self.assertEqual(self.output_stream.getvalue(), "")

        self.output_event_handlers = [self.stream_printer_event_handler]
        self.assertTrue(self.stream_printer_event_handler.receive_event(test % self.__class__.__name__, new_val, [log_atom.raw_data, log_atom.raw_data], None, log_atom, self))
        self.assertEqual(self.output_stream.getvalue(), exp % (dt, match_s1 + ", " + match_s2, "b' pid='", self.__class__.__name__, description, 2, "   pid=\n   pid=\n"))
        self.reset_output_stream()

        # test suppress detector list
        self.output_event_handlers = None
        self.analysis_context.suppress_detector_list = [description]
        self.assertTrue(self.stream_printer_event_handler.receive_event(test % self.__class__.__name__, new_val, [log_atom.raw_data, log_atom.raw_data], None, log_atom, self))
        self.assertEqual(self.output_stream.getvalue(), "")

        self.output_event_handlers = [self.stream_printer_event_handler]
        self.analysis_context.suppress_detector_list = []
        self.assertTrue(self.stream_printer_event_handler.receive_event(test % self.__class__.__name__, new_val, [log_atom.raw_data, log_atom.raw_data], None, log_atom, self))
        self.assertEqual(self.output_stream.getvalue(), exp % (dt, match_s1 + ", " + match_s2, "b' pid='", self.__class__.__name__, description, 2, "   pid=\n   pid=\n"))

    def test2validate_parameters(self):
        """Test all initialization parameters for the event handler. Input parameters must be validated in the class."""
        self.assertRaises(TypeError, StreamPrinterEventHandler, self.analysis_context, "")
        self.assertRaises(TypeError, StreamPrinterEventHandler, self.analysis_context, b"")
        self.assertRaises(TypeError, StreamPrinterEventHandler, self.analysis_context, ["default"])
        self.assertRaises(TypeError, StreamPrinterEventHandler, self.analysis_context, None)
        self.assertRaises(TypeError, StreamPrinterEventHandler, self.analysis_context, True)
        self.assertRaises(TypeError, StreamPrinterEventHandler, self.analysis_context, 123)
        self.assertRaises(TypeError, StreamPrinterEventHandler, self.analysis_context, 123.3)
        self.assertRaises(TypeError, StreamPrinterEventHandler, self.analysis_context, {"id": "Default"})
        self.assertRaises(TypeError, StreamPrinterEventHandler, self.analysis_context, ())
        self.assertRaises(TypeError, StreamPrinterEventHandler, self.analysis_context, set())
        StreamPrinterEventHandler(self.analysis_context, sys.stdout)
        StreamPrinterEventHandler(self.analysis_context, sys.stderr)
        StreamPrinterEventHandler(self.analysis_context, self.output_stream)


if __name__ == "__main__":
    unittest.main()
