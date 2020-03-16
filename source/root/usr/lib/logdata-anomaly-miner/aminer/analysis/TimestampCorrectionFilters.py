"""This file collects various classes useful to filter and correct
the timestamp associated with a received parsed atom."""

from aminer.input import AtomHandlerInterface
import time
from datetime import datetime


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
    timestamp = log_atom.getTimestamp()
    if timestamp is None:
      timestamp = time.time()
    if isinstance(timestamp, datetime):
      timestamp = (datetime.fromtimestamp(0)-timestamp).total_seconds()
    if timestamp < self.latest_timestamp_seen:
      log_atom.setTimestamp(self.latest_timestamp_seen)
    else:
      self.latest_timestamp_seen = timestamp

    result = False
    for handler in self.subhandler_list:
      handler_result = handler.receive_atom(log_atom)
      if handler_result is True:
        result = True
        if self.stop_when_handled_flag:
          break
    return result
