import unittest
from aminer.parsing.MatchContext import MatchContext
from aminer.parsing.FixedDataModelElement import FixedDataModelElement
from time import time, sleep
from aminer.input.LogAtom import LogAtom
from aminer.parsing.ParserMatch import ParserMatch
from aminer.events.DefaultMailNotificationEventHandler import DefaultMailNotificationEventHandler
import subprocess
from unit.TestBase import TestBase
from datetime import datetime


class DefaultMailNotificationEventHandlerTest(TestBase):
    __expected_string = '%s New value for pathes %s: %s\n%s: "%s" (%d lines)\n  %s'
    mail_call = 'echo p | mail -u root'
    mail_call = 'echo p | mail -u mail'
    
    pid = b' pid='
    test = 'Test.%s'
    datetime_format_string = '%Y-%m-%d %H:%M:%S'

    '''
    In this test case multiple lines should be received, before sending an email to root@localhost.
    Make sure no mail notifications are in /var/spool/mail/root, before running this test.
    This test case must wait some time to ensure, that the mail can be read.
    '''
    def test1log_multiple_lines_event(self):
      description = "Test1DefaultMailNotificationEventHandler"
      self.match_context = MatchContext(self.pid)
      self.fixed_dme = FixedDataModelElement('s1', self.pid)
      self.match_element = self.fixed_dme.get_match_element("match", self.match_context)

      self.match_context = MatchContext(self.pid)
      self.fixed_dme2 = FixedDataModelElement('s2', self.pid)
      self.match_element2 = self.fixed_dme2.get_match_element("match", self.match_context)

      self.default_mail_notification_event_handler = DefaultMailNotificationEventHandler(self.analysis_context)
      self.analysis_context.register_component(self, description)

      t = time()
      self.log_atom = LogAtom(self.fixed_dme.fixed_data, ParserMatch(self.match_element), t, self)
      self.default_mail_notification_event_handler.receive_event(self.test % self.__class__.__name__, \
          'New value for pathes %s, %s: %s' % ('match/s1', 'match/s2',
          repr(self.match_element.match_object)), [self.log_atom.raw_data, self.log_atom.raw_data], None, self.log_atom, self)

      t += 600
      self.log_atom = LogAtom(self.fixed_dme.fixed_data, ParserMatch(self.match_element), t, self)
      sleep(10)
      self.default_mail_notification_event_handler.receive_event(self.test % self.__class__.__name__, \
          'New value for pathes %s, %s: %s' % ('match/s1', 'match/s2',
          repr(self.match_element.match_object)), [self.log_atom.raw_data, self.log_atom.raw_data], None, self.log_atom, self)
      sleep(30)
      result = subprocess.run(self.mail_call, shell=True, stdout=subprocess.PIPE)

      self.assertTrue(self.__expected_string % (datetime.fromtimestamp(t-600).strftime(self.datetime_format_string),
        "" + self.match_element.get_path() + ", " + self.match_element2.get_path(), self.match_element.get_match_object(),
        self.__class__.__name__, description, 2, self.match_element.get_match_string().decode("utf-8") +
        "\n  " + self.match_element2.get_match_string().decode("utf-8")) in str(result.stdout, 'utf-8'), msg="%s vs \n %s" % (self.__expected_string %
        (datetime.fromtimestamp(t).strftime(self.datetime_format_string),
        self.match_element.get_path(), self.match_element.get_match_object(),
        self.__class__.__name__, description, 1, self.match_element.get_match_string().decode("utf-8") +
        "\n\n"), str(result.stdout, 'utf-8')))

      self.assertTrue(self.__expected_string %
        (datetime.fromtimestamp(t).strftime(self.datetime_format_string),
        "" + self.match_element.get_path() + ", " + self.match_element2.get_path(), self.match_element.get_match_object(),
        self.__class__.__name__, description, 2, self.match_element.get_match_string().decode("utf-8") +
        "\n  " + self.match_element2.get_match_string().decode("utf-8") + "\n\n") in str(result.stdout, 'utf-8'))
    
    '''
    In this test case the functionality of the timer is tested.
    The eventCollectTime must not be 0!
    '''
    def test2do_timer(self):
      description = "Test2DefaultMailNotificationEventHandler"
      self.default_mail_notification_event_handler = DefaultMailNotificationEventHandler(self.analysis_context)
      self.analysis_context.register_component(self, description)

      t = time()
      self.match_context = MatchContext(self.pid)
      self.fixed_dme = FixedDataModelElement('s3', self.pid)
      self.match_element = self.fixed_dme.get_match_element("match", self.match_context)

      self.log_atom = LogAtom(self.fixed_dme.fixed_data, ParserMatch(self.match_element), t, self)
      self.default_mail_notification_event_handler.receive_event(self.test % self.__class__.__name__, \
          'New value for pathes %s: %s' % ('match/s3',
          repr(self.match_element.match_object)), [self.log_atom.raw_data], None, self.log_atom, self)

      t = 0
      self.default_mail_notification_event_handler.do_timer(t)
      result = subprocess.run(self.mail_call, shell=True, stdout=subprocess.PIPE)

      self.assertFalse(self.__expected_string %
        (datetime.fromtimestamp(t).strftime(self.datetime_format_string),
        self.match_element.get_path(), self.match_element.get_match_object(),
        self.__class__.__name__, description, 1, self.match_element.get_match_string().decode("utf-8") +
        "\n\n") in str(result.stdout, 'utf-8'))

      t = time()
      self.default_mail_notification_event_handler.next_alert_time = t + 500
      self.default_mail_notification_event_handler.do_timer(t)

      sleep(5)
      result = subprocess.run(self.mail_call, shell=True, stdout=subprocess.PIPE)
      self.assertFalse(self.__expected_string %
        (datetime.fromtimestamp(t).strftime(self.datetime_format_string),
        self.match_element.get_path(), self.match_element.get_match_object(),
        self.__class__.__name__, description, 1, self.match_element.get_match_string().decode("utf-8") +
        "\n\n") in str(result.stdout, 'utf-8'))

      self.default_mail_notification_event_handler.next_alert_time = t
      self.default_mail_notification_event_handler.do_timer(t)

      sleep(30)
      result = subprocess.run(self.mail_call, shell=True, stdout=subprocess.PIPE)
      self.assertTrue(self.__expected_string %
        (datetime.fromtimestamp(t).strftime(self.datetime_format_string),
        self.match_element.get_path(), self.match_element.get_match_object(),
        self.__class__.__name__, description, 1, self.match_element.get_match_string().decode("utf-8") +
        "\n\n") in str(result.stdout, 'utf-8'), msg="%s vs \n %s" % (self.__expected_string %
        (datetime.fromtimestamp(t).strftime(self.datetime_format_string), self.match_element.get_path(), self.match_element.get_match_object(),
        self.__class__.__name__, description, 1, self.match_element.get_match_string().decode("utf-8") +
        "\n\n"), str(result.stdout, 'utf-8')))


if __name__ == "__main__":
    unittest.main()