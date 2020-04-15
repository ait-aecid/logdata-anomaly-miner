"""This module defines a handler that forwards unparsed atoms
to the event handlers."""

from aminer.input import AtomHandlerInterface
from aminer.parsing import DebugMatchContext

class VerboseUnparsedAtomHandler(AtomHandlerInterface):
  """Handlers of this class will forward received unparsed
  atoms to the registered event handlers applying the
  DebugMatchContext."""

  def __init__(self, event_handlers, parsing_model):
    self.event_handlers = event_handlers
    self.parsing_model = parsing_model
    self.persistence_id = None

  def receive_atom(self, log_atom):
    """Receive an unparsed atom to create events for each."""
    if log_atom.is_parsed():
      return False
    match_context = DebugMatchContext(log_atom.raw_data)
    self.parsing_model.get_match_element('', match_context)
    event_data = dict()
    debug_info = match_context.get_debug_info()
    debug_lines = []
    for line in debug_info.split('\n'):
      debug_lines.append(line.strip())
    event_data['DebugLog'] = debug_lines
    for listener in self.event_handlers:
      listener.receive_event('Input.VerboseUnparsedAtomHandler', 'Unparsed atom received',
        [debug_info + log_atom.raw_data.decode()], event_data, log_atom, self)
    return True
