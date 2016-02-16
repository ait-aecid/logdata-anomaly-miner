import email
import os
import subprocess
import sys
import time

from aminer.parsing import MatchElement


class StreamPrinterEventHandler:
  """This class implements an event record listener, that will
just print out data about the event to a stream, by default this
is stdout"""
  def __init__(self, aminerConfig):
    pass

  def receiveEvent(self, eventType, eventMessage, sortedLogLines, eventData):
    """Receive information about a detected event."""
    message='%s (%d lines)\n' % (eventMessage, len(sortedLogLines))
    for line in sortedLogLines:
      message+='  '+line+'\n'
    if eventData!=None:
      if isinstance(eventData, MatchElement.MatchElement):
        message+='  '+eventData.annotateMatch('')+'\n'
      else:
        message+='  '+str(eventData)+'\n'
    print '%s' % message
    sys.stdout.flush()
    return


  def checkTriggers(self):
    return
