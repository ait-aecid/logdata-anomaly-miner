"""This module defines an event handler that prints data to
a stream."""

import sys

from aminer.events import EventHandlerInterface
from aminer.input.LogAtom import LogAtom


class StreamPrinterEventHandler(EventHandlerInterface):
  """This class implements an event record listener, that will
just print out data about the event to a stream, by default this
is stdout"""
  def __init__(self, aminerConfig, stream=sys.stdout):
    self.stream = stream

  def receiveEvent(self, eventType, eventMessage, sortedLogLines, eventData,
                   eventSource):
    """Receive information about a detected event."""
    message = '%s (%d lines)\n' % (eventMessage, len(sortedLogLines))
    for line in sortedLogLines:
      message += '  '+repr(line)[2:-1]+'\n'
    if eventData is not None:
      if isinstance(eventData, LogAtom):
        message += '  [%s/%s]' % (eventData.getTimestamp(), eventData.source)
        if eventData.parserMatch is not None:
          message += ' '+eventData.parserMatch.matchElement.annotateMatch('')+'\n'
      else:
        message += '  '+repr(eventData)+'\n'
    print('%s' % message, file=self.stream)
    self.stream.flush()
    return
