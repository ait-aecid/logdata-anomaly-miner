"""This module defines the event handler for reporting via emails."""

import email.mime.text
import os
import tempfile
import subprocess  # skipcq: BAN-B404
import shlex
import sys
import time
import re

from aminer.AnalysisChild import AnalysisContext
from aminer.util import TimeTriggeredComponentInterface
from aminer.events import EventHandlerInterface
from aminer.events.EventData import EventData


class DefaultMailNotificationEventHandler(EventHandlerInterface, TimeTriggeredComponentInterface):
    """This class implements an event record listener, that will pool received events, reduce the amount of events below the maximum
    number allowed per timeframe, create text representation of received events and send them via "sendmail" transport."""

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
            raise Exception('Cannot create e-mail notification listener without target address')
        self.sender_address = shlex.quote(
            aminer_config.config_properties.get(DefaultMailNotificationEventHandler.CONFIG_KEY_MAIL_FROM_ADDRESS))
        if not is_email.match(self.recipient_address) or not is_email.match(self.sender_address):
            raise Exception('MailAlerting.TargetAddress and MailAlerting.FromAddress must be email addresses!')

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

        # Locate the sendmail binary immediately at startup to avoid delayed errors due to misconfiguration.
        self.sendmail_binary_path = '/usr/sbin/sendmail'
        if not os.path.exists(self.sendmail_binary_path):
            raise Exception('sendmail binary not found')
        self.running_sendmail_processes = []

    def receive_event(self, event_type, event_message, sorted_log_lines, event_data, log_atom, event_source):
        """Receive information about a detected event."""
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
            self.current_message += shlex.quote(event_data_obj.receive_event_string())

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
        """Get the trigger class this component can be registered for. See AnalysisContext class for different trigger classes
        available."""
        return AnalysisContext.TIME_TRIGGER_CLASS_REALTIME

    def do_timer(self, trigger_time):
        """Check exit status of previous mail sending procedures and check if alerts should be sent."""
        # Cleanup old sendmail processes.
        if self.running_sendmail_processes:
            running_processes = []
            for process in self.running_sendmail_processes:
                process.poll()
                if process.returncode is None:
                    running_processes.append(process)
                    continue
                if process.returncode != 0:
                    print('WARNING: Sending mail terminated with error %d' % process.returncode, file=sys.stderr)
            self.running_sendmail_processes = running_processes

        if (self.next_alert_time != 0) and (trigger_time >= self.next_alert_time):
            self.send_notification(trigger_time)
        return 10

    def send_notification(self, trigger_time):
        """Really send out the message."""
        if self.events_collected == 0:
            return

        # Write whole message to file to allow sendmail send it asynchronously.
        message_tmp_file = tempfile.TemporaryFile()
        message = email.mime.text.MIMEText(self.current_message)
        subject_text = '%s Collected Events' % self.subject_prefix
        if self.last_alert_time != 0:
            subject_text += ' in the last %d seconds' % (trigger_time - self.last_alert_time)
        message['Subject'] = subject_text
        if self.sender_address is not None:
            message['From'] = self.sender_address
        message['To'] = self.recipient_address
        message_tmp_file.write(message.as_bytes())

        # Rewind before handling over the fd to sendmail.
        message_tmp_file.seek(0)

        sendmail_args = ['sendmail']
        if self.sender_address is not None:
            sendmail_args += ['-f', self.sender_address]
        sendmail_args.append(self.recipient_address)
        # Start the sendmail process. Use close_fds to avoid leaking of any open file descriptors to the new client.
        # skipcq: BAN-B603
        process = subprocess.Popen(sendmail_args, executable=self.sendmail_binary_path, stdin=message_tmp_file, close_fds=True)
        # Just append the process to the list of running processes. It will remain in zombie state until next invocation of list cleanup.
        self.running_sendmail_processes.append(process)
        message_tmp_file.close()

        self.last_alert_time = trigger_time
        self.events_collected = 0
        self.current_message = ''
        self.next_alert_time = 0
