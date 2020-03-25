"""This module dfines a writer that forwards match information
to a stream."""

from aminer.AnalysisChild import AnalysisContext
from aminer.input import AtomHandlerInterface
from aminer.util import TimeTriggeredComponentInterface
import _io

class MatchValueStreamWriter(AtomHandlerInterface, TimeTriggeredComponentInterface):
  """This class extracts values from a given match and writes
  them to a stream. This can be used to forward these values to
  another program (when stream is a wrapped network socket) or
  to a file for further analysis. A stream is used instead of
  a file descriptor to increase performance. To flush it from
  time to time, add the writer object also to the time trigger
  list."""

  def __init__(self, stream, match_value_path_list, separator_string, missing_value_string):
    """Initialize the writer."""
    self.stream = stream
    self.match_value_path_list = match_value_path_list
    self.separator_string = separator_string
    self.missing_value_string = missing_value_string

  def receive_atom(self, log_atom):
    """Forward match value information to the stream."""
    match_dict = log_atom.parser_match.get_match_dictionary()
    add_sep_flag = False
    contains_data = False
    result = b''
    for path in self.match_value_path_list:
      if add_sep_flag:
        result += self.separator_string
      match = match_dict.get(path, None)
      if match is None:
        result += self.missing_value_string
      else:
        result += match.match_string
        contains_data = True
      add_sep_flag = True
    if contains_data:
      if not isinstance(self.stream, _io.BytesIO):
        self.stream.write(result.decode('ascii', 'ignore'))
        self.stream.write('\n')
      else:
        self.stream.write(result)
        self.stream.write(b'\n')


  def get_time_trigger_class(self):
    """Get the trigger class this component should be registered
    for. This trigger is used only for persistency, so real-time
    triggering is needed."""
    return AnalysisContext.TIME_TRIGGER_CLASS_REALTIME

  def do_timer(self, trigger_time):
    """Flush the timer."""
    self.stream.flush()
    return 10

  def do_persist(self):
    """Flush the timer."""
    self.stream.flush()
