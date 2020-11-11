import unittest
from aminer.parsing.MatchContext import MatchContext
from aminer.parsing.FixedDataModelElement import FixedDataModelElement
from time import time
from aminer.input.LogAtom import LogAtom
from aminer.parsing.ParserMatch import ParserMatch
from aminer.events.DefaultMailNotificationEventHandler import DefaultMailNotificationEventHandler
# skipcq: BAN-B404
import subprocess
from unit.TestBase import TestBase
from datetime import datetime


class DefaultMailNotificationEventHandlerTest(TestBase):
    """Unittests for the DefaultMailNotificationEventHandler."""

    __expected_string = '%s New value for pathes %s: %s\n%s: "%s" (%d lines)\n  %s'
    mail_call = 'echo p | mail -u root'
    mail_call = 'echo p | mail -u mail'

    pid = b' pid='
    test = 'Test.%s'
    datetime_format_string = '%Y-%m-%d %H:%M:%S'

    def test1log_multiple_lines_event(self):
        """
        In this test case multiple lines should be received, before sending an email to root@localhost.
        Make sure no mail notifications are in /var/spool/mail/root, before running this test. This test case must wait some time to
        ensure, that the mail can be read.
        """
        description = "Test1DefaultMailNotificationEventHandler"
        match_context = MatchContext(self.pid)
        fixed_dme = FixedDataModelElement('s1', self.pid)
        match_element = fixed_dme.get_match_element("match", match_context)

        match_context = MatchContext(self.pid)
        fixed_dme2 = FixedDataModelElement('s2', self.pid)
        match_element2 = fixed_dme2.get_match_element("match", match_context)

        default_mail_notification_event_handler = DefaultMailNotificationEventHandler(self.analysis_context)
        self.analysis_context.register_component(self, description)

        t = time()
        log_atom = LogAtom(fixed_dme.fixed_data, ParserMatch(match_element), t, self)
        default_mail_notification_event_handler.receive_event(
            self.test % self.__class__.__name__, 'New value for pathes %s, %s: %s' % (
                'match/s1', 'match/s2', repr(match_element.match_object)), [log_atom.raw_data, log_atom.raw_data], None, log_atom, self)

        t += 600
        log_atom = LogAtom(fixed_dme.fixed_data, ParserMatch(match_element), t, self)
        # set the next_alert_time instead of sleeping 10 seconds
        default_mail_notification_event_handler.next_alert_time = time()
        default_mail_notification_event_handler.receive_event(
            self.test % self.__class__.__name__, 'New value for pathes %s, %s: %s' % (
                'match/s1', 'match/s2', repr(match_element.match_object)), [log_atom.raw_data, log_atom.raw_data], None, log_atom, self)
        # skipcq: PYL-W1510, BAN-B602
        result = subprocess.run(self.mail_call, shell=True, stdout=subprocess.PIPE)

        self.assertTrue(self.__expected_string % (
            datetime.fromtimestamp(t - 600).strftime(self.datetime_format_string), "" + match_element.get_path() + ", " +
            match_element2.get_path(), match_element.get_match_object(), self.__class__.__name__, description, 2,
            match_element.get_match_string().decode() + "\n  " + match_element2.get_match_string().decode()) in
            str(result.stdout, 'utf-8'), msg="%s vs \n %s" % (self.__expected_string % (
                datetime.fromtimestamp(t).strftime(self.datetime_format_string), match_element.get_path(), match_element.get_match_object(),
                self.__class__.__name__, description, 1, match_element.get_match_string().decode() + "\n\n"),
                str(result.stdout, 'utf-8')))

        self.assertTrue(self.__expected_string % (
            datetime.fromtimestamp(t).strftime(self.datetime_format_string), "" + match_element.get_path() + ", " +
            match_element2.get_path(), match_element.get_match_object(), self.__class__.__name__, description, 2,
            match_element.get_match_string().decode() + "\n  " + match_element2.get_match_string().decode() + "\n\n") in
                str(result.stdout, 'utf-8'))

    def test2do_timer(self):
        """In this test case the functionality of the timer is tested. The eventCollectTime must not be 0."""
        description = "Test2DefaultMailNotificationEventHandler"
        default_mail_notification_event_handler = DefaultMailNotificationEventHandler(self.analysis_context)
        self.analysis_context.register_component(self, description)

        t = time()
        match_context = MatchContext(self.pid)
        fixed_dme = FixedDataModelElement('s3', self.pid)
        match_element = fixed_dme.get_match_element("match", match_context)

        log_atom = LogAtom(fixed_dme.fixed_data, ParserMatch(match_element), t, self)
        default_mail_notification_event_handler.receive_event(
            self.test % self.__class__.__name__, 'New value for pathes %s: %s' % (
                'match/s3', repr(match_element.match_object)), [log_atom.raw_data], None, log_atom, self)

        t = 0
        default_mail_notification_event_handler.do_timer(t)
        # skipcq: PYL-W1510, BAN-B602
        result = subprocess.run(self.mail_call, shell=True, stdout=subprocess.PIPE)

        self.assertFalse(self.__expected_string % (
            datetime.fromtimestamp(t).strftime(self.datetime_format_string), match_element.get_path(), match_element.get_match_object(),
            self.__class__.__name__, description, 1, match_element.get_match_string().decode() + "\n\n") in str(result.stdout, 'utf-8'))

        t = time()
        default_mail_notification_event_handler.next_alert_time = t + 500
        default_mail_notification_event_handler.do_timer(t)

        # skipcq: PYL-W1510, BAN-B602
        result = subprocess.run(self.mail_call, shell=True, stdout=subprocess.PIPE)
        self.assertFalse(self.__expected_string % (
            datetime.fromtimestamp(t).strftime(self.datetime_format_string), match_element.get_path(), match_element.get_match_object(),
            self.__class__.__name__, description, 1, match_element.get_match_string().decode() + "\n\n") in str(result.stdout, 'utf-8'))

        default_mail_notification_event_handler.next_alert_time = t
        default_mail_notification_event_handler.do_timer(t)

        # skipcq: PYL-W1510, BAN-B602
        result = subprocess.run(self.mail_call, shell=True, stdout=subprocess.PIPE)
        self.assertTrue(self.__expected_string % (
            datetime.fromtimestamp(t).strftime(self.datetime_format_string), match_element.get_path(), match_element.get_match_object(),
            self.__class__.__name__, description, 1, match_element.get_match_string().decode() + "\n\n") in
            str(result.stdout, 'utf-8'), msg="%s vs \n %s" % (self.__expected_string % (
                datetime.fromtimestamp(t).strftime(self.datetime_format_string), match_element.get_path(), match_element.get_match_object(),
                self.__class__.__name__, description, 1, match_element.get_match_string().decode() + "\n\n"), str(result.stdout, 'utf-8')))

    def test3check_email_addresses(self):
        """Test if mail addresses are validated as expected."""
        ac = self.analysis_context
        ac.aminer_config.config_properties[DefaultMailNotificationEventHandler.CONFIG_KEY_MAIL_TARGET_ADDRESS] = "test123@gmail.com"
        ac.aminer_config.config_properties[DefaultMailNotificationEventHandler.CONFIG_KEY_MAIL_FROM_ADDRESS] = "test123@gmail.com"
        _ = DefaultMailNotificationEventHandler(ac)
        ac.aminer_config.config_properties[DefaultMailNotificationEventHandler.CONFIG_KEY_MAIL_TARGET_ADDRESS] = "root@localhost"
        ac.aminer_config.config_properties[DefaultMailNotificationEventHandler.CONFIG_KEY_MAIL_FROM_ADDRESS] = "root@localhost"
        _ = DefaultMailNotificationEventHandler(ac)
        ac.aminer_config.config_properties[DefaultMailNotificationEventHandler.CONFIG_KEY_MAIL_TARGET_ADDRESS] = "domain.user1@localhost"
        self.assertRaises(Exception, DefaultMailNotificationEventHandler, ac)
        ac.aminer_config.config_properties[DefaultMailNotificationEventHandler.CONFIG_KEY_MAIL_FROM_ADDRESS] = "domain.user1@localhost"
        self.assertRaises(Exception, DefaultMailNotificationEventHandler, ac)
        ac.aminer_config.config_properties[DefaultMailNotificationEventHandler.CONFIG_KEY_MAIL_TARGET_ADDRESS] = "root@notLocalhost"
        ac.aminer_config.config_properties[DefaultMailNotificationEventHandler.CONFIG_KEY_MAIL_FROM_ADDRESS] = "root@localhost"
        self.assertRaises(Exception, DefaultMailNotificationEventHandler, ac)
        ac.aminer_config.config_properties[DefaultMailNotificationEventHandler.CONFIG_KEY_MAIL_TARGET_ADDRESS] = "root@localhost"
        ac.aminer_config.config_properties[DefaultMailNotificationEventHandler.CONFIG_KEY_MAIL_FROM_ADDRESS] = "root@notLocalhost"
        self.assertRaises(Exception, DefaultMailNotificationEventHandler, ac)


if __name__ == "__main__":
    unittest.main()
