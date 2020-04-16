"""This file collects various classes useful to filter and correct
the timestamp associated with a received parsed atom."""

from aminer.input import AtomHandlerInterface
import time


class SimpleMonotonicTimestampAdjust(AtomHandlerInterface):
  """Handlers of this class compare the timestamp of a newly received
  atom with the largest timestamp seen so far. When below, the
  timestamp of this atom is adjusted to the largest value seen,
  otherwise the largest value seen is updated."""
  def __init__(self, subhandler_list, stop_when_handled_flag=False):
    self.subhandler_list = subhandler_list
    self.stop_when_handled_flag = stop_when_handled_flag
    self.latest_timestamp_seen = 0

  def receive_atom(self, log_atom):
    """Pass the atom to the subhandlers.
    @return false when no subhandler was able to handle the atom."""
    if log_atom.get_timestamp() is not None:
      if log_atom.get_timestamp() < self.latest_timestamp_seen:
        log_atom.set_timestamp(self.latest_timestamp_seen)
      else:
        self.latest_timestamp_seen = log_atom.get_timestamp()

    result = False
    for handler in self.subhandler_list:
      handler_result = handler.receive_atom(log_atom)
      if handler_result is True:
        result = True
        if self.stop_when_handled_flag:
          break
    return result
