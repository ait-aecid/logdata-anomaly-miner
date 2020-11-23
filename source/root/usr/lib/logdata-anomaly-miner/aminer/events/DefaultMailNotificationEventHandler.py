"""
This module defines the event handler for reporting via emails.

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.
This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with
this program. If not, see <http://www.gnu.org/licenses/>.
"""

import shlex
import time
import re
from smtplib import SMTP, SMTPException
import logging

from aminer import AMinerConfig
from aminer.AnalysisChild import AnalysisContext
from aminer.util import TimeTriggeredComponentInterface
from aminer.events import EventHandlerInterface
from aminer.events.EventData import EventData


_message_str = """From: %s
To: %s
Subject: %s

%s
"""


class DefaultMailNotificationEventHandler(EventHandlerInterface, TimeTriggeredComponentInterface):
    """
    This class implements an event record listener.
    It will pool received events, reduce the amount of events below the maximum number allowed per timeframe, create text representation
    of received events and send them via "sendmail" transport.
    """

    CONFIG_KEY_MAIL_TARGET_ADDRESS = 'MailAlerting.TargetAddress'
    CONFIG_KEY_MAIL_FROM_ADDRESS = 'MailAlerting.FromAddress'
    CONFIG_KEY_MAIL_SUBJECT_PREFIX = 'MailAlerting.SubjectPrefix'
    CONFIG_KEY_MAIL_ALERT_GRACE_TIME = 'MailAlerting.AlertGraceTime'
    CONFIG_KEY_EVENT_COLLECT_TIME = 'MailAlerting.EventCollectTime'
    CONFIG_KEY_ALERT_MIN_GAP = 'MailAlerting.MinAlertGap'
    CONFIG_KEY_ALERT_MAX_GAP = 'MailAlerting.MaxAlertGap'
    CONFIG_KEY_ALERT_MAX_EVENTS_PER_MESSAGE = 'MailAlerting.MaxEventsPerMessage'

    def __init__(self, analysis_context):
        self.analysis_context = analysis_context
        aminer_config = analysis_context.aminer_config
        # @see https://emailregex.com/
        is_email = re.compile(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)|^[a-zA-Z0-9]+@localhost$")
        self.recipient_address = shlex.quote(
            aminer_config.config_properties.get(DefaultMailNotificationEventHandler.CONFIG_KEY_MAIL_TARGET_ADDRESS))
        if self.recipient_address is None:
            msg = 'Cannot create e-mail notification listener without target address'
            logging.getLogger(AMinerConfig.DEBUG_LOG_NAME).error(msg)
            raise Exception(msg)
        self.sender_address = shlex.quote(
            aminer_config.config_properties.get(DefaultMailNotificationEventHandler.CONFIG_KEY_MAIL_FROM_ADDRESS))
        if not is_email.match(self.recipient_address) or not is_email.match(self.sender_address):
            msg = 'MailAlerting.TargetAddress and MailAlerting.FromAddress must be email addresses!'
            logging.getLogger(AMinerConfig.DEBUG_LOG_NAME).error(msg)
            raise Exception(msg)

        self.subject_prefix = shlex.quote(
            aminer_config.config_properties.get(DefaultMailNotificationEventHandler.CONFIG_KEY_MAIL_SUBJECT_PREFIX, 'AMiner Alerts:'))
        self.alert_grace_time_end = aminer_config.config_properties.get(
            DefaultMailNotificationEventHandler.CONFIG_KEY_MAIL_ALERT_GRACE_TIME, 0)
        self.event_collect_time = aminer_config.config_properties.get(DefaultMailNotificationEventHandler.CONFIG_KEY_EVENT_COLLECT_TIME, 10)
        self.min_alert_gap = aminer_config.config_properties.get(DefaultMailNotificationEventHandler.CONFIG_KEY_ALERT_MIN_GAP, 600)
        self.max_alert_gap = aminer_config.config_properties.get(DefaultMailNotificationEventHandler.CONFIG_KEY_ALERT_MAX_GAP, 600)
        self.max_events_per_message = aminer_config.config_properties.get(
            DefaultMailNotificationEventHandler.CONFIG_KEY_ALERT_MAX_EVENTS_PER_MESSAGE, 1000)
        if self.alert_grace_time_end > 0:
            self.alert_grace_time_end += time.time()
        self.events_collected = 0
        self.event_collection_start_time = 0
        self.last_alert_time = 0
        self.next_alert_time = 0
        self.current_alert_gap = self.min_alert_gap
        self.current_message = ''

    def receive_event(self, event_type, event_message, sorted_log_lines, event_data, log_atom, event_source):
        """Receive information about a detected event."""
        if event_source.output_event_handlers is not None and self not in event_source.output_event_handlers:
            return
        if self.alert_grace_time_end != 0:
            if self.alert_grace_time_end >= time.time():
                return
            self.alert_grace_time_end = 0

        # Avoid too many calls to the operating system time()
        current_time = time.time()

        if self.events_collected < self.max_events_per_message:
            if self.events_collected == 0:
                self.event_collection_start_time = current_time
            self.events_collected += 1
            event_data_obj = EventData(event_type, event_message, sorted_log_lines, event_data, log_atom, event_source,
                                       self.analysis_context)
            self.current_message += event_data_obj.receive_event_string()

        if self.next_alert_time == 0:
            if self.last_alert_time != 0:
                # This is the first event received after sending of a previous notification. If the currentAlertGap has not elapsed,
                # increase the gap immediately.
                self.next_alert_time = self.last_alert_time + self.current_alert_gap
                if self.next_alert_time < current_time:
                    # We are already out of the required gap.
                    self.current_alert_gap = self.min_alert_gap
                    self.last_alert_time = 0
                    self.next_alert_time = current_time + self.event_collect_time
                else:
                    # Increase the gap
                    self.current_alert_gap *= 1.5
                    if self.current_alert_gap > self.max_alert_gap:
                        self.current_alert_gap = self.max_alert_gap
            else:
                # No relevant last alert time recorded, just use default.
                self.next_alert_time = current_time + self.event_collect_time

        if (self.next_alert_time != 0) and (current_time >= self.next_alert_time):
            self.send_notification(current_time)

    def get_time_trigger_class(self):
        """
        Get the trigger class this component can be registered for.
        See AnalysisContext class for different trigger classes available.
        """
        return AnalysisContext.TIME_TRIGGER_CLASS_REALTIME

    def do_timer(self, trigger_time):
        """Check exit status of previous mail sending procedures and check if alerts should be sent."""
        if (self.next_alert_time != 0) and (trigger_time >= self.next_alert_time):
            self.send_notification(trigger_time)
        return 10

    def send_notification(self, trigger_time):
        """Really send out the message."""
        if self.events_collected == 0:
            return
        subject_text = '%s Collected Events' % self.subject_prefix
        if self.last_alert_time != 0:
            subject_text += ' in the last %d seconds' % (trigger_time - self.last_alert_time)
        message = _message_str % (self.sender_address, self.recipient_address, subject_text, self.current_message)
        try:
            # timeout explicitly needs to be set None, because in python version < 3.7 socket.settimeout() sets the socket type
            # SOCK_NONBLOCKING and the code fails.
            smtp_obj = SMTP('127.0.0.1', port=25, timeout=5)
            smtp_obj.sendmail(self.sender_address, self.recipient_address, message)
            smtp_obj.quit()
        except SMTPException as e:
            print(e)
            # here logging is needed, but cannot be implemented yet.
        self.last_alert_time = trigger_time
        self.events_collected = 0
        self.current_message = ''
        self.next_alert_time = 0
        logging.getLogger(AMinerConfig.DEBUG_LOG_NAME).debug('%s sent notification.', self.__class__.__name__)
