from aminer.events import EventHandlerInterface
from aminer.util import LogarithmicBackoffHistory

class VolatileLogarithmicBackoffEventHistory(EventHandlerInterface, LogarithmicBackoffHistory):
  """This class is a volatile filter to keep a history of received
  events, e.g. for analysis by other components or for external
  access via remote control interface."""

  def __init__(self, maxItems):
    """Initialize the history component."""
    LogarithmicBackoffHistory.__init__(self, maxItems)

  def receiveEvent(self, eventType, eventMessage, sortedLogLines,
      eventData, eventSource):
    """Receive information about a detected event and store all
    related data as tuple to the history log."""
    self.addObject((eventType, eventMessage, sortedLogLines, eventData, eventSource))
    return(True)
