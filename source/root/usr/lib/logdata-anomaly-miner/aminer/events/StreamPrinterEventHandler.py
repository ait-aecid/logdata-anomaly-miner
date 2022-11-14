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

from aminer.events.EventInterfaces import EventHandlerInterface
from aminer.events.EventData import EventData


class StreamPrinterEventHandler(EventHandlerInterface):
    """
    This class implements an event record listener, that will just print out data about the event to a stream.
    By default this is stdout.
    """

    def __init__(self, analysis_context, stream=sys.stdout):
        """
        Initialize the event handler.
        @param analysis_context the analysis context used to get the component.
        @param stream the output stream of the event handler.
        """
        self.analysis_context = analysis_context
        self.stream = stream

    def receive_event(self, event_type, event_message, sorted_loglines, event_data, log_atom, event_source):
        """
        Receive information about a detected event.
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
        event_data_obj = EventData(event_type, event_message, sorted_loglines, event_data, log_atom, event_source, self.analysis_context)
        message = f'{event_data_obj.receive_event_string()}\n'
        if hasattr(self.stream, 'buffer'):
            self.stream.buffer.write(message.encode())
        else:
            self.stream.write(message)
        self.stream.flush()
