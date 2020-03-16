"""This module defines an event handler that prints data to
a stream."""

import sys

from aminer.events import EventHandlerInterface
from aminer.events.EventData import EventData

class StreamPrinterEventHandler(EventHandlerInterface):
  """This class implements an event record listener, that will
just print out data about the event to a stream, by default this
is stdout"""
  def __init__(self, analysisContext, stream=sys.stdout):
    self.analysisContext = analysisContext
    self.stream = stream

  def receive_event(self, eventType, eventMessage, sortedLogLines, eventData, logAtom,
                    eventSource):
    """Receive information about a detected event."""
    self.eventData = EventData(eventType, eventMessage, sortedLogLines, eventData, logAtom, eventSource, self.analysisContext)
    message = self.eventData.receiveEventString()
    print('%s' % message, file=self.stream)
    self.stream.flush()
    return
