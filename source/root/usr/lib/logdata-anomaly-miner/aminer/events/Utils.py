"""This module defines a handler for storing event history."""

from aminer.events import EventHandlerInterface
from aminer.util import LogarithmicBackoffHistory


class VolatileLogarithmicBackoffEventHistory(EventHandlerInterface, LogarithmicBackoffHistory):
  """This class is a volatile filter to keep a history of received
  events, e.g. for analysis by other components or for external
  access via remote control interface."""

  def __init__(self, max_items):
    """Initialize the history component."""
    LogarithmicBackoffHistory.__init__(self, max_items)
    self.event_id = 0

  def receive_event(self, event_type, event_message, sorted_log_lines, event_data,
                    log_atom, event_source):
    """Receive information about a detected event and store all
    related data as tuple to the history log."""
    self.add_object((self.event_id, event_type, event_message, sorted_log_lines, event_data, log_atom, event_source))
    self.event_id += 1
    return True
