"""This module defines a handler that forwards unparsed atoms
to the event handlers."""

from aminer.input import AtomHandlerInterface

class SimpleUnparsedAtomHandler(AtomHandlerInterface):
  """Handlers of this class will just forward received unparsed
  atoms to the registered event handlers."""

  def __init__(self, event_handlers):
    self.event_handlers = event_handlers
    self.persistence_id = None

  def receive_atom(self, log_atom):
    """Receive an unparsed atom to create events for each."""
    if log_atom.is_parsed():
      return False
    event_data = {}
    for listener in self.event_handlers:
      listener.receive_event('Input.UnparsedAtomHandler', \
          'Unparsed atom received', [log_atom.raw_data], event_data, log_atom, self)
    return True
