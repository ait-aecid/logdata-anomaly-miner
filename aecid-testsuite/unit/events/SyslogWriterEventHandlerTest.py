import unittest
import os
from datetime import datetime
from time import time, sleep
from aminer.events.SyslogWriterEventHandler import SyslogWriterEventHandler
from aminer.input.LogAtom import LogAtom
from aminer.parsing.ParserMatch import ParserMatch
from unit.TestBase import TestBase, DummyFixedDataModelElement, DummyMatchContext


class SyslogWriterEventHandlerTest(TestBase):
    """Some of the test cases may fail if the same numbers as the PID are found in the syslog. Rerun the unit, when this happens."""

    def test1receive_event(self):
        """In this test case the EventHandler receives multiple lines from the test class."""
        description = "Test1SyslogWriterEventHandler"
        pid = b" pid="
        test = "Test.%s" % self.__class__.__name__
        match_context = DummyMatchContext(pid)
        fdme = DummyFixedDataModelElement("s1", pid)
        match_element = fdme.get_match_element("match", match_context)
        new_val = "New value for paths match/s1, match/s2: b' pid='"
        t = time()
        dtm = datetime.fromtimestamp(t).strftime("%Y-%m-%d %H:%M:%S")
        exp1 = '[0] %s %s\n[0-1] %s: "%s" (%d lines)\n[0-2]    pid=\n[0-3]    pid=\n' % (dtm, new_val, self.__class__.__name__, description, 2)
        exp2 = '[1] %s %s\n[1-1] %s: "%s" (%d lines)\n' % (dtm, new_val, self.__class__.__name__, description, 0)

        sweh = SyslogWriterEventHandler(self.analysis_context, "aminer")
        self.analysis_context.register_component(self, description)
        log_atom = LogAtom(fdme.data, ParserMatch(match_element), t, self)
        sweh.receive_event(test, new_val, [log_atom.raw_data, log_atom.raw_data], None, log_atom, self)
        string = self.extract_syslog_string()
        found = False
        string = string.split("Syslog logger initialized\n")
        for log in string:
            if exp1 in log:
                found = True
        self.assertTrue(found)

        # In this test case the EventHandler receives no lines from the test class.
        sweh.receive_event(test, new_val, [], None, log_atom, self)
        string = self.extract_syslog_string()
        found = False
        string = string.split("Syslog logger initialized\n")

        for log in string:
            if exp2 in log:
                found = True
        self.assertTrue(found)

        # In this test case the EventHandler receives no logAtom from the test class and the class should raise an exception.
        self.assertRaises(Exception, sweh.receive_event, test, new_val, [log_atom.raw_data, log_atom.raw_data], log_atom.get_parser_match(), self)

        # test output_event_handlers
        self.output_event_handlers = []
        self.assertTrue(sweh.receive_event(test, new_val, [log_atom.raw_data, log_atom.raw_data], None, log_atom, self))
        string = self.extract_syslog_string()
        self.assertEqual(string.count("\n"), 7)

        self.output_event_handlers = [sweh]
        self.assertTrue(sweh.receive_event(test, new_val, [log_atom.raw_data, log_atom.raw_data], None, log_atom, self))
        string = self.extract_syslog_string()
        self.assertEqual(string.count("\n"), 11)

        # test suppress detector list
        self.output_event_handlers = None
        self.analysis_context.suppress_detector_list = [description]
        self.assertTrue(sweh.receive_event(test, new_val, [log_atom.raw_data, log_atom.raw_data], None, log_atom, self))
        string = self.extract_syslog_string()
        self.assertEqual(string.count("\n"), 11)

        self.output_event_handlers = [sweh]
        self.analysis_context.suppress_detector_list = []
        self.assertTrue(sweh.receive_event(test, new_val, [log_atom.raw_data, log_atom.raw_data], None, log_atom, self))
        string = self.extract_syslog_string()
        self.assertEqual(string.count("\n"), 15)

    def extract_syslog_string(self):
        string = ""
        sleep(0.2)
        with open("/var/log/syslog") as search:
            for line in search:
                line = line.rstrip()  # remove "\n" at end of line
                if "aminer[" + str(os.getpid()) + "]" in line:
                    line = line.split("]: ")
                    string += (line[1]) + "\n"
        return string

    def test2validate_parameters(self):
        """Test all initialization parameters for the event handler. Input parameters must be validated in the class."""
        self.assertRaises(TypeError, SyslogWriterEventHandler, self.analysis_context, ["default"])
        self.assertRaises(TypeError, SyslogWriterEventHandler, self.analysis_context, None)
        self.assertRaises(TypeError, SyslogWriterEventHandler, self.analysis_context, b"Default")
        self.assertRaises(TypeError, SyslogWriterEventHandler, self.analysis_context, True)
        self.assertRaises(TypeError, SyslogWriterEventHandler, self.analysis_context, 123)
        self.assertRaises(TypeError, SyslogWriterEventHandler, self.analysis_context, 123.3)
        self.assertRaises(TypeError, SyslogWriterEventHandler, self.analysis_context, {"id": "Default"})
        self.assertRaises(TypeError, SyslogWriterEventHandler, self.analysis_context, ())
        self.assertRaises(TypeError, SyslogWriterEventHandler, self.analysis_context, set())
        self.assertRaises(ValueError, SyslogWriterEventHandler, self.analysis_context, "")
        SyslogWriterEventHandler(self.analysis_context, "aminer")

if __name__ == "__main__":
    unittest.main()
