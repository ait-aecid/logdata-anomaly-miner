from aminer.util import LogarithmicBackoffHistory
from aminer.parsing import ParsedAtomHandlerInterface


class VolatileLogarithmicBackoffParsedAtomHistory(ParsedAtomHandlerInterface, LogarithmicBackoffHistory):
  """This class is a volatile filter to keep a history of atom
  and match data objects, e.g. for analysis by other components
  or for external access via remote control interface."""

  def __init__(self, maxItems):
    """Initialize the history component."""
    LogarithmicBackoffHistory.__init__(self, maxItems)


  def receiveParsedAtom(self, atomData, match):
    """Receive an atom and match and add both as tuple to the
    history log."""
    self.addObject((atomData, match))
    return(True)
