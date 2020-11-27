"""
This module defines an event handler that prints data to a stream.

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

import sys

from aminer.events import EventHandlerInterface
from aminer.events.EventData import EventData


class StreamPrinterEventHandler(EventHandlerInterface):
    """
    This class implements an event record listener, that will just print out data about the event to a stream.
    By default this is stdout.
    """

    def __init__(self, analysis_context, stream=sys.stdout):
        self.analysis_context = analysis_context
        self.stream = stream

    def receive_event(self, event_type, event_message, sorted_log_lines, event_data, log_atom, event_source):
        """Receive information about a detected event."""
        component_name = self.analysis_context.get_name_by_component(event_source)
        if component_name in self.analysis_context.suppress_detector_list:
            return
        event_data_obj = EventData(event_type, event_message, sorted_log_lines, event_data, log_atom, event_source, self.analysis_context)
        message = '%s\n' % event_data_obj.receive_event_string()
        if hasattr(self.stream, 'buffer'):
            self.stream.buffer.write(message.encode())
        else:
            self.stream.write(message)
        self.stream.flush()
