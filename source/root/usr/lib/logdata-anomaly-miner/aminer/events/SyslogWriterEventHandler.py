"""This module defines an event handler that prints data to
a local syslog instance."""

import io
import os
import syslog

from aminer.events import EventHandlerInterface
from aminer.events import StreamPrinterEventHandler


class SyslogWriterEventHandler(EventHandlerInterface):
    """This class implements an event record listener to forward events to the local syslog instance.
    CAVEAT: USE THIS AT YOUR OWN RISK: by creating aminer/syslog log data processing loops, you will flood your syslog and probably
    fill up your disks."""

    def __init__(self, analysis_context, instance_name='aminer'):
        self.instanceName = instance_name
        syslog.openlog('%s[%d]' % (self.instanceName, os.getpid()), syslog.LOG_INFO, syslog.LOG_DAEMON)
        syslog.syslog(syslog.LOG_INFO, 'Syslog logger initialized')
        self.buffer_stream = io.StringIO()
        self.event_writer = StreamPrinterEventHandler(analysis_context, self.buffer_stream)
        self.event_id = 0

    def receive_event(self, event_type, event_message, sorted_log_lines, event_data, log_atom, event_source):
        """Receive information about a detected even and forward it to syslog."""
        self.buffer_stream.seek(0)
        self.buffer_stream.truncate(0)
        self.event_writer.receive_event(event_type, event_message, sorted_log_lines, event_data, log_atom, event_source)
        event_data = self.buffer_stream.getvalue()
        current_event_id = self.event_id
        self.event_id += 1
        serial = 0
        for data_line in event_data.strip().split('\n'):
            # Python syslog is very ugly if lines are too long, so break them down.
            while data_line:
                message = None
                if serial == 0:
                    message = '[%d] %s' % (current_event_id, data_line[:800])
                else:
                    message = '[%d-%d] %s' % (current_event_id, serial, data_line[:800])
                data_line = data_line[800:]
                syslog.syslog(syslog.LOG_INFO, message)
                serial += 1
