"""This module defines a handler that forwards unparsed atoms
to the event handlers."""

from aminer.input import AtomHandlerInterface

class SimpleUnparsedAtomHandler(AtomHandlerInterface):
  """Handlers of this class will just forward received unparsed
  atoms to the registered event handlers."""

  def __init__(self, eventHandlers):
    self.eventHandlers = eventHandlers

  def receiveAtom(self, logAtom):
    """Receive an unparsed atom to create events for each."""
    if logAtom.isParsed():
      return False
    for listener in self.eventHandlers:
      listener.receiveEvent('Input.UnparsedAtomHandler', \
          'Unparsed atom received', [logAtom.rawData], logAtom, self)
    return True
