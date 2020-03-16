"""This module defines a handler that forwards unparsed atoms
to the event handlers."""

from aminer.input import AtomHandlerInterface

class SimpleUnparsedAtomHandler(AtomHandlerInterface):
  """Handlers of this class will just forward received unparsed
  atoms to the registered event handlers."""

  def __init__(self, eventHandlers):
    self.eventHandlers = eventHandlers
    self.persistenceId = None

  def receive_atom(self, logAtom):
    """Receive an unparsed atom to create events for each."""
    if logAtom.isParsed():
      return False
    eventData = dict()
    for listener in self.eventHandlers:
      listener.receive_event('Input.UnparsedAtomHandler', \
          'Unparsed atom received', [logAtom.rawData], eventData, logAtom, self)
    return True
