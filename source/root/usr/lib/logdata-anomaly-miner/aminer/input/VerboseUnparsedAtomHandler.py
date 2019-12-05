"""This module defines a handler that forwards unparsed atoms
to the event handlers."""

from aminer.input import AtomHandlerInterface
from aminer.parsing import DebugMatchContext

class VerboseUnparsedAtomHandler(AtomHandlerInterface):
  """Handlers of this class will forward received unparsed
  atoms to the registered event handlers applying the
  DebugMatchContext."""

  def __init__(self, eventHandlers, parsingModel):
    self.eventHandlers = eventHandlers
    self.parsingModel = parsingModel

  def receiveAtom(self, logAtom):
    """Receive an unparsed atom to create events for each."""
    if logAtom.isParsed():
      return False
    matchContext = DebugMatchContext(logAtom.rawData)
    self.parsingModel.getMatchElement('', matchContext)
    for listener in self.eventHandlers:
      listener.receiveEvent('Input.UnparsedAtomHandler', \
          ('Unparsed atom received\n%s\n' % (matchContext.getDebugInfo())), \
          [logAtom.rawData], [logAtom], self)
    return True
