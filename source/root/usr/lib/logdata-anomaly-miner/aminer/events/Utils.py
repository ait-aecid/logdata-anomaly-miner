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

from aminer.events import EventHandlerInterface
from aminer.util import LogarithmicBackoffHistory


class VolatileLogarithmicBackoffEventHistory(EventHandlerInterface, LogarithmicBackoffHistory):
    """
    This class is a volatile filter to keep a history of received events.
    Example usages are for analysis by other components or for external access via remote control interface.
    """

    def __init__(self, max_items):
        """Initialize the history component."""
        LogarithmicBackoffHistory.__init__(self, max_items)
        self.event_id = 0

    def receive_event(self, event_type, event_message, sorted_log_lines, event_data, log_atom, event_source):
        """Receive information about a detected event and store all related data as tuple to the history log."""
        self.add_object((self.event_id, event_type, event_message, sorted_log_lines, event_data, log_atom, event_source))
        self.event_id += 1
        return True
