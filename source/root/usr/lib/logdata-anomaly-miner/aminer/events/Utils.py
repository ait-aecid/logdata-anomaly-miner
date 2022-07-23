"""
This module defines a handler for storing event history.

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

from aminer.events.EventInterfaces import EventHandlerInterface
from aminer.util.History import LogarithmicBackoffHistory


class VolatileLogarithmicBackoffEventHistory(EventHandlerInterface, LogarithmicBackoffHistory):
    """
    This class is a volatile filter to keep a history of received events.
    Example usages are for analysis by other components or for external access via remote control interface.
    """

    def __init__(self, max_items):
        """
        Initialize the history component.
        @param max_items the maximum number of items in the event history.
        """
        LogarithmicBackoffHistory.__init__(self, max_items)
        self.event_id = 0

    def receive_event(self, event_type, event_message, sorted_loglines, event_data, log_atom, event_source):
        """
        Receive information about a detected event and store all related data as tuple to the history log.
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
        self.add_object((self.event_id, event_type, event_message, sorted_loglines, event_data, log_atom, event_source))
        self.event_id += 1
        return True
