"""
This module defines an event handler that prints data to a local syslog instance.

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

import io
import os
import syslog

from aminer.events.EventInterfaces import EventHandlerInterface
from aminer.events.StreamPrinterEventHandler import StreamPrinterEventHandler


class SyslogWriterEventHandler(EventHandlerInterface):
    """
    This class implements an event record listener to forward events to the local syslog instance.
    CAVEAT: USE THIS AT YOUR OWN RISK: by creating aminer/syslog log data processing loops, you will flood your syslog and probably
    fill up your disks.
    """

    def __init__(self, analysis_context, instance_name='aminer'):
        """
        Initialize the event handler.
        @param analysis_context the analysis context used to get the component.
        @param instance_name the process name shown in the syslog.
        """
        self.analysis_context = analysis_context
        self.instanceName = instance_name
        syslog.openlog(f'{self.instanceName}[{os.getpid()}]', syslog.LOG_INFO, syslog.LOG_DAEMON)
        syslog.syslog(syslog.LOG_INFO, 'Syslog logger initialized')
        self.buffer_stream = io.StringIO()
        self.event_writer = StreamPrinterEventHandler(analysis_context, self.buffer_stream)
        self.event_id = 0

    def receive_event(self, event_type, event_message, sorted_loglines, event_data, log_atom, event_source):
        """
        Receive information about a detected even and forward it to syslog.
        @param event_type is a string with the event type class this event belongs to. This information can be used to interpret
               type-specific event_data objects. Together with the eventMessage and sorted_loglines, this can be used to create generic log
               messages.
        @param event_message the first output line of the event.
        @param sorted_loglines sorted list of log lines that were considered when generating the event, as far as available to the time
               of the event. The list has to contain at least one line.
        @param event_data type-specific event data object, should not be used unless listener really knows about the event_type.
        @param log_atom the log atom which produced the event.
        @param event_source reference to detector generating the event.
        """
        if hasattr(event_source, 'output_event_handlers') and event_source.output_event_handlers is not None and self not in \
                event_source.output_event_handlers:
            return
        component_name = self.analysis_context.get_name_by_component(event_source)
        if component_name in self.analysis_context.suppress_detector_list:
            return
        self.buffer_stream.seek(0)
        self.buffer_stream.truncate(0)
        self.event_writer.receive_event(event_type, event_message, sorted_loglines, event_data, log_atom, event_source)
        event_data = self.buffer_stream.getvalue()
        current_event_id = self.event_id
        self.event_id += 1
        serial = 0
        for data_line in event_data.strip().split('\n'):
            # Python syslog is very ugly if lines are too long, so break them down.
            while data_line:
                message = None
                if serial == 0:
                    message = f'[{current_event_id}] {data_line[:800]}'
                else:
                    message = f'[{current_event_id}-{serial}] {data_line[:800]}'
                data_line = data_line[800:]
                syslog.syslog(syslog.LOG_INFO, message)
                serial += 1
