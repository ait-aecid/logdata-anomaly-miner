import unittest
import sys
import subprocess
from time import time, sleep
from aminer.input.LogAtom import LogAtom
from aminer.parsing.ParserMatch import ParserMatch
from aminer.events.DefaultMailNotificationEventHandler import DefaultMailNotificationEventHandler
from unit.TestBase import TestBase, DummyFixedDataModelElement, DummyMatchContext
from datetime import datetime


class DefaultMailNotificationEventHandlerTest(TestBase):
    """Unittests for the DefaultMailNotificationEventHandler."""

    __expected_string = '%s New value for paths %s: %s\n%s: "%s" (%d lines)\n  %s'
    mail_call = "echo p | mail -u mail"
    mail_delete_call = "echo d | mail -u mail"

    pid = b" pid="
    test = "Test.%s"
    dtf = "%Y-%m-%d %H:%M:%S"

    def test1receive_event(self):
        """
        In this test case multiple lines should be received, before sending an email to root@localhost.
        Make sure no mail notifications are in /var/spool/mail/root, before running this test. This test case must wait some time to
        ensure, that the mail can be read.
        """
        description = "Test1DefaultMailNotificationEventHandler"
        match_context = DummyMatchContext(self.pid)
        fixed_dme = DummyFixedDataModelElement("s1", self.pid)
        match_element = fixed_dme.get_match_element("match", match_context)

        dmneh = DefaultMailNotificationEventHandler(self.analysis_context)
        self.analysis_context.register_component(self, description)

        t = time()
        log_atom = LogAtom(fixed_dme.data, ParserMatch(match_element), t, self)
        dmneh.receive_event(self.test % self.__class__.__name__, "New value for paths %s, %s: %s" % (
            "match/s1", "match/s2", repr(match_element.match_object)), [log_atom.raw_data, log_atom.raw_data], None, log_atom, self)

        t += 600
        log_atom = LogAtom(fixed_dme.data, ParserMatch(match_element), t, self)
        # set the next_alert_time instead of sleeping 10 seconds
        dmneh.next_alert_time = time()
        dmneh.receive_event(self.test % self.__class__.__name__, "New value for paths %s, %s: %s" % (
                "match/s1", "match/s2", repr(match_element.match_object)), [log_atom.raw_data, log_atom.raw_data], None, log_atom, self)
        sleep(1)
        result = subprocess.run(self.mail_call, shell=True, stdout=subprocess.PIPE)
        subprocess.run(self.mail_delete_call, shell=True, stdout=subprocess.PIPE)

        exp = self.__expected_string % ("", "match/s1, match/s2", "b' pid='", self.__class__.__name__, description, 2, " pid=\n   pid=")
        exp1 = datetime.fromtimestamp(t - 600).strftime(self.dtf) + exp
        exp2 = datetime.fromtimestamp(t).strftime(self.dtf) + exp
        self.assertTrue(exp1 + "\n" + exp2 + "\n\n" in str(result.stdout, "utf-8"), msg="%s vs \n %s" % (exp1 + "\n\n", str(result.stdout, "utf-8")))

        # test output_event_handlers
        self.output_event_handlers = []
        dmneh.next_alert_time = time()
        self.assertTrue(dmneh.receive_event(self.test % self.__class__.__name__, "New value for paths %s, %s: %s" % (
            "match/s1", "match/s2", repr(match_element.match_object)), [log_atom.raw_data, log_atom.raw_data], None, log_atom, self))
        sleep(1)
        result = subprocess.run(self.mail_call, shell=True, stdout=subprocess.PIPE)
        self.assertTrue("0 messages" in str(result.stdout, "utf-8"))

        self.output_event_handlers = [dmneh]
        dmneh.next_alert_time = time()
        self.assertTrue(dmneh.receive_event(self.test % self.__class__.__name__, "New value for paths %s, %s: %s" % (
            "match/s1", "match/s2", repr(match_element.match_object)), [log_atom.raw_data, log_atom.raw_data], None, log_atom, self))
        sleep(1)
        result = subprocess.run(self.mail_call, shell=True, stdout=subprocess.PIPE)
        subprocess.run(self.mail_delete_call, shell=True, stdout=subprocess.PIPE)
        self.assertTrue(exp2 in str(result.stdout, "utf-8"))

        # test suppress detector list
        self.output_event_handlers = None
        self.analysis_context.suppress_detector_list = [description]
        dmneh.next_alert_time = time()
        self.assertTrue(dmneh.receive_event(self.test % self.__class__.__name__, "New value for paths %s, %s: %s" % (
            "match/s1", "match/s2", repr(match_element.match_object)), [log_atom.raw_data, log_atom.raw_data], None, log_atom, self))
        sleep(2)
        result = subprocess.run(self.mail_call, shell=True, stdout=subprocess.PIPE)
        self.assertTrue("0 messages" in str(result.stdout, "utf-8"))

        self.output_event_handlers = [dmneh]
        self.analysis_context.suppress_detector_list = []
        dmneh.next_alert_time = time()
        self.assertTrue(dmneh.receive_event(self.test % self.__class__.__name__, "New value for paths %s, %s: %s" % (
            "match/s1", "match/s2", repr(match_element.match_object)), [log_atom.raw_data, log_atom.raw_data], None, log_atom, self))
        sleep(1)
        result = subprocess.run(self.mail_call, shell=True, stdout=subprocess.PIPE)
        subprocess.run(self.mail_delete_call, shell=True, stdout=subprocess.PIPE)
        self.assertTrue(exp2 in str(result.stdout, "utf-8"))

    def test2do_timer(self):
        """In this test case the functionality of the timer is tested. The eventCollectTime must not be 0."""
        description = "Test2DefaultMailNotificationEventHandler"
        dmneh = DefaultMailNotificationEventHandler(self.analysis_context)
        self.analysis_context.register_component(self, description)

        t = time()
        match_context = DummyMatchContext(self.pid)
        fixed_dme = DummyFixedDataModelElement("s3", self.pid)
        match_element = fixed_dme.get_match_element("match", match_context)

        log_atom = LogAtom(fixed_dme.data, ParserMatch(match_element), t, self)
        dmneh.receive_event(self.test % self.__class__.__name__, "New value for paths %s: %s" % (
            "match/s3", repr(match_element.match_object)), [log_atom.raw_data], None, log_atom, self)

        t = 0
        dmneh.do_timer(t)
        result = subprocess.run(self.mail_call, shell=True, stdout=subprocess.PIPE)

        exp = self.__expected_string % ("", "match/s3", "b' pid='", self.__class__.__name__, description, 1, " pid=") + "\n\n"
        exp1 = datetime.fromtimestamp(t).strftime(self.dtf) + exp
        self.assertFalse(exp1 in str(result.stdout, "utf-8"))

        t = time()
        dmneh.next_alert_time = t + 500
        dmneh.do_timer(t)

        exp2 = datetime.fromtimestamp(t).strftime(self.dtf) + exp
        result = subprocess.run(self.mail_call, shell=True, stdout=subprocess.PIPE)
        self.assertFalse(exp2 in str(result.stdout, "utf-8"))

        dmneh.next_alert_time = t
        dmneh.do_timer(t)

        sleep(2)
        result = subprocess.run(self.mail_call, shell=True, stdout=subprocess.PIPE)
        subprocess.run(self.mail_delete_call, shell=True, stdout=subprocess.PIPE)
        self.assertTrue(exp2 in str(result.stdout, "utf-8"))

    def test3validate_parameters(self):
        """Test all initialization parameters for the event handler. Input parameters must be validated in the class."""
        d = DefaultMailNotificationEventHandler
        ac = self.analysis_context
        acp = self.analysis_context.aminer_config.config_properties
        acp[d.CONFIG_KEY_MAIL_TARGET_ADDRESS] = "test123@gmail.com"
        acp[d.CONFIG_KEY_MAIL_FROM_ADDRESS] = "test123@gmail.com"
        acp[d.CONFIG_KEY_MAIL_SUBJECT_PREFIX] = "test prefix"
        acp[d.CONFIG_KEY_MAIL_ALERT_GRACE_TIME] = 0
        acp[d.CONFIG_KEY_EVENT_COLLECT_TIME] = 0
        acp[d.CONFIG_KEY_ALERT_MIN_GAP] = 0
        acp[d.CONFIG_KEY_ALERT_MAX_GAP] = 600
        acp[d.CONFIG_KEY_ALERT_MAX_EVENTS_PER_MESSAGE] = 1
        DefaultMailNotificationEventHandler(ac)

        acp[d.CONFIG_KEY_MAIL_SUBJECT_PREFIX] = True
        self.assertRaises(TypeError, d, ac)
        acp[d.CONFIG_KEY_MAIL_SUBJECT_PREFIX] = 123
        self.assertRaises(TypeError, d, ac)
        acp[d.CONFIG_KEY_MAIL_SUBJECT_PREFIX] = 123.3
        self.assertRaises(TypeError, d, ac)
        acp[d.CONFIG_KEY_MAIL_SUBJECT_PREFIX] = {"id": "Default"}
        self.assertRaises(TypeError, d, ac)
        acp[d.CONFIG_KEY_MAIL_SUBJECT_PREFIX] = ()
        self.assertRaises(TypeError, d, ac)
        acp[d.CONFIG_KEY_MAIL_SUBJECT_PREFIX] = set()
        self.assertRaises(TypeError, d, ac)
        acp[d.CONFIG_KEY_MAIL_SUBJECT_PREFIX] = b""
        self.assertRaises(TypeError, d, ac)
        acp[d.CONFIG_KEY_MAIL_SUBJECT_PREFIX] = ["Default"]
        self.assertRaises(TypeError, d, ac)
        acp[d.CONFIG_KEY_MAIL_SUBJECT_PREFIX] = None
        self.assertRaises(TypeError, d, ac)
        acp[d.CONFIG_KEY_MAIL_SUBJECT_PREFIX] = ""
        DefaultMailNotificationEventHandler(ac)

        acp[d.CONFIG_KEY_MAIL_ALERT_GRACE_TIME] = True
        self.assertRaises(TypeError, d, ac)
        acp[d.CONFIG_KEY_MAIL_ALERT_GRACE_TIME] = ["Default"]
        self.assertRaises(TypeError, d, ac)
        acp[d.CONFIG_KEY_MAIL_ALERT_GRACE_TIME] = {"id": "Default"}
        self.assertRaises(TypeError, d, ac)
        acp[d.CONFIG_KEY_MAIL_ALERT_GRACE_TIME] = ()
        self.assertRaises(TypeError, d, ac)
        acp[d.CONFIG_KEY_MAIL_ALERT_GRACE_TIME] = set()
        self.assertRaises(TypeError, d, ac)
        acp[d.CONFIG_KEY_MAIL_ALERT_GRACE_TIME] = ""
        self.assertRaises(TypeError, d, ac)
        acp[d.CONFIG_KEY_MAIL_ALERT_GRACE_TIME] = b""
        self.assertRaises(TypeError, d, ac)
        acp[d.CONFIG_KEY_MAIL_ALERT_GRACE_TIME] = None
        self.assertRaises(TypeError, d, ac)
        acp[d.CONFIG_KEY_MAIL_ALERT_GRACE_TIME] = -1
        self.assertRaises(ValueError, d, ac)
        acp[d.CONFIG_KEY_MAIL_ALERT_GRACE_TIME] = 123
        DefaultMailNotificationEventHandler(ac)
        acp[d.CONFIG_KEY_MAIL_ALERT_GRACE_TIME] = 123.3
        DefaultMailNotificationEventHandler(ac)

        acp[d.CONFIG_KEY_EVENT_COLLECT_TIME] = True
        self.assertRaises(TypeError, d, ac)
        acp[d.CONFIG_KEY_EVENT_COLLECT_TIME] = ["Default"]
        self.assertRaises(TypeError, d, ac)
        acp[d.CONFIG_KEY_EVENT_COLLECT_TIME] = {"id": "Default"}
        self.assertRaises(TypeError, d, ac)
        acp[d.CONFIG_KEY_EVENT_COLLECT_TIME] = ()
        self.assertRaises(TypeError, d, ac)
        acp[d.CONFIG_KEY_EVENT_COLLECT_TIME] = set()
        self.assertRaises(TypeError, d, ac)
        acp[d.CONFIG_KEY_EVENT_COLLECT_TIME] = ""
        self.assertRaises(TypeError, d, ac)
        acp[d.CONFIG_KEY_EVENT_COLLECT_TIME] = b""
        self.assertRaises(TypeError, d, ac)
        acp[d.CONFIG_KEY_EVENT_COLLECT_TIME] = None
        self.assertRaises(TypeError, d, ac)
        acp[d.CONFIG_KEY_EVENT_COLLECT_TIME] = -1
        self.assertRaises(ValueError, d, ac)
        acp[d.CONFIG_KEY_EVENT_COLLECT_TIME] = 123
        DefaultMailNotificationEventHandler(ac)
        acp[d.CONFIG_KEY_EVENT_COLLECT_TIME] = 123.3
        DefaultMailNotificationEventHandler(ac)

        acp[d.CONFIG_KEY_ALERT_MIN_GAP] = True
        self.assertRaises(TypeError, d, ac)
        acp[d.CONFIG_KEY_ALERT_MIN_GAP] = ["Default"]
        self.assertRaises(TypeError, d, ac)
        acp[d.CONFIG_KEY_ALERT_MIN_GAP] = {"id": "Default"}
        self.assertRaises(TypeError, d, ac)
        acp[d.CONFIG_KEY_ALERT_MIN_GAP] = ()
        self.assertRaises(TypeError, d, ac)
        acp[d.CONFIG_KEY_ALERT_MIN_GAP] = set()
        self.assertRaises(TypeError, d, ac)
        acp[d.CONFIG_KEY_ALERT_MIN_GAP] = ""
        self.assertRaises(TypeError, d, ac)
        acp[d.CONFIG_KEY_ALERT_MIN_GAP] = b""
        self.assertRaises(TypeError, d, ac)
        acp[d.CONFIG_KEY_ALERT_MIN_GAP] = None
        self.assertRaises(TypeError, d, ac)
        acp[d.CONFIG_KEY_ALERT_MIN_GAP] = -1
        self.assertRaises(ValueError, d, ac)
        acp[d.CONFIG_KEY_ALERT_MIN_GAP] = 123
        DefaultMailNotificationEventHandler(ac)
        acp[d.CONFIG_KEY_ALERT_MIN_GAP] = 123.3
        DefaultMailNotificationEventHandler(ac)

        acp[d.CONFIG_KEY_ALERT_MAX_GAP] = True
        self.assertRaises(TypeError, d, ac)
        acp[d.CONFIG_KEY_ALERT_MAX_GAP] = ["Default"]
        self.assertRaises(TypeError, d, ac)
        acp[d.CONFIG_KEY_ALERT_MAX_GAP] = {"id": "Default"}
        self.assertRaises(TypeError, d, ac)
        acp[d.CONFIG_KEY_ALERT_MAX_GAP] = ()
        self.assertRaises(TypeError, d, ac)
        acp[d.CONFIG_KEY_ALERT_MAX_GAP] = set()
        self.assertRaises(TypeError, d, ac)
        acp[d.CONFIG_KEY_ALERT_MAX_GAP] = ""
        self.assertRaises(TypeError, d, ac)
        acp[d.CONFIG_KEY_ALERT_MAX_GAP] = b""
        self.assertRaises(TypeError, d, ac)
        acp[d.CONFIG_KEY_ALERT_MAX_GAP] = None
        self.assertRaises(TypeError, d, ac)
        acp[d.CONFIG_KEY_ALERT_MAX_GAP] = -1
        self.assertRaises(ValueError, d, ac)
        acp[d.CONFIG_KEY_ALERT_MAX_GAP] = 600
        DefaultMailNotificationEventHandler(ac)
        acp[d.CONFIG_KEY_ALERT_MAX_GAP] = 600.3
        DefaultMailNotificationEventHandler(ac)

        acp[d.CONFIG_KEY_ALERT_MIN_GAP] = 0
        acp[d.CONFIG_KEY_ALERT_MAX_GAP] = 0
        DefaultMailNotificationEventHandler(ac)
        acp[d.CONFIG_KEY_ALERT_MIN_GAP] = 1
        self.assertRaises(ValueError, d, ac)
        acp[d.CONFIG_KEY_ALERT_MIN_GAP] = 0

        acp[d.CONFIG_KEY_ALERT_MAX_EVENTS_PER_MESSAGE] = True
        self.assertRaises(TypeError, d, ac)
        acp[d.CONFIG_KEY_ALERT_MAX_EVENTS_PER_MESSAGE] = ["Default"]
        self.assertRaises(TypeError, d, ac)
        acp[d.CONFIG_KEY_ALERT_MAX_EVENTS_PER_MESSAGE] = {"id": "Default"}
        self.assertRaises(TypeError, d, ac)
        acp[d.CONFIG_KEY_ALERT_MAX_EVENTS_PER_MESSAGE] = ()
        self.assertRaises(TypeError, d, ac)
        acp[d.CONFIG_KEY_ALERT_MAX_EVENTS_PER_MESSAGE] = set()
        self.assertRaises(TypeError, d, ac)
        acp[d.CONFIG_KEY_ALERT_MAX_EVENTS_PER_MESSAGE] = ""
        self.assertRaises(TypeError, d, ac)
        acp[d.CONFIG_KEY_ALERT_MAX_EVENTS_PER_MESSAGE] = b""
        self.assertRaises(TypeError, d, ac)
        acp[d.CONFIG_KEY_ALERT_MAX_EVENTS_PER_MESSAGE] = None
        self.assertRaises(TypeError, d, ac)
        acp[d.CONFIG_KEY_ALERT_MAX_EVENTS_PER_MESSAGE] = 0
        self.assertRaises(ValueError, d, ac)
        acp[d.CONFIG_KEY_ALERT_MAX_EVENTS_PER_MESSAGE] = 123
        DefaultMailNotificationEventHandler(ac)
        acp[d.CONFIG_KEY_ALERT_MAX_EVENTS_PER_MESSAGE] = 123.3
        DefaultMailNotificationEventHandler(ac)

        # Test if mail addresses are validated as expected.
        acp[d.CONFIG_KEY_MAIL_TARGET_ADDRESS] = "root@localhost"
        acp[d.CONFIG_KEY_MAIL_FROM_ADDRESS] = "root@localhost"
        DefaultMailNotificationEventHandler(ac)
        acp[d.CONFIG_KEY_MAIL_TARGET_ADDRESS] = "domain.user1@localhost"
        self.assertRaises(ValueError, d, ac)
        acp[d.CONFIG_KEY_MAIL_FROM_ADDRESS] = "domain.user1@localhost"
        self.assertRaises(ValueError, DefaultMailNotificationEventHandler, ac)
        acp[d.CONFIG_KEY_MAIL_TARGET_ADDRESS] = "root@notLocalhost"
        acp[d.CONFIG_KEY_MAIL_FROM_ADDRESS] = "root@localhost"
        self.assertRaises(ValueError, d, ac)
        acp[d.CONFIG_KEY_MAIL_TARGET_ADDRESS] = "root@localhost"
        acp[d.CONFIG_KEY_MAIL_FROM_ADDRESS] = "root@notLocalhost"
        self.assertRaises(ValueError, d, ac)


if __name__ == "__main__":
    unittest.main()
