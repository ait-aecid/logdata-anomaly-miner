"""This module defines an event handler that prints data to
a stream."""

import sys

from aminer.events import EventHandlerInterface
from aminer.events.EventData import EventData

class StreamPrinterEventHandler(EventHandlerInterface):
  """This class implements an event record listener, that will
just print out data about the event to a stream, by default this
is stdout"""
  def __init__(self, analysis_context, stream=sys.stdout):
    self.analysis_context = analysis_context
    self.stream = stream

  def receive_event(self, event_type, event_message, sorted_log_lines, event_data, log_atom,
                    event_source):
    """Receive information about a detected event."""
    self.event_data = EventData(event_type, event_message, sorted_log_lines, event_data, log_atom, event_source, self.analysis_context)
    message = self.event_data.receive_event_string()
    print('%s' % message, file=self.stream)
    self.stream.flush()
