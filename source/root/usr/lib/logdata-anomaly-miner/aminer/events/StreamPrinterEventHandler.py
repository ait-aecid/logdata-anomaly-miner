import email
import os
import subprocess
import sys
import time

from aminer.events import EventHandlerInterface
from aminer.parsing import MatchElement


class StreamPrinterEventHandler(EventHandlerInterface):
  """This class implements an event record listener, that will
just print out data about the event to a stream, by default this
is stdout"""
  def __init__(self, aminerConfig, stream=sys.stdout):
    self.stream=stream

  def receiveEvent(self, eventType, eventMessage, sortedLogLines, eventData):
    """Receive information about a detected event."""
    message='%s (%d lines)\n' % (eventMessage, len(sortedLogLines))
    for line in sortedLogLines:
      message+='  '+line+'\n'
    if eventData!=None:
      if isinstance(eventData, MatchElement):
        message+='  '+eventData.annotateMatch('')+'\n'
      else:
        message+='  '+str(eventData)+'\n'
    print >>self.stream, '%s' % message
    self.stream.flush()
    return
