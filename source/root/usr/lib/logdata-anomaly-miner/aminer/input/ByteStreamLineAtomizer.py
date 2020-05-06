"""This module provides support for splitting a data stream into
atoms, perform parsing and forward the results."""

from aminer.input.LogAtom import LogAtom
from aminer.input import StreamAtomizer
from aminer.parsing import MatchContext
from aminer.parsing import ParserMatch


class ByteStreamLineAtomizer(StreamAtomizer):
  """This atomizer consumes binary data from a stream to break
  it into lines, removing the line separator at the end. With
  a parsing model, it will also perform line parsing. Failures
  in atomizing or parsing will cause events to be generated and
  sent to event handler.
  Data will be consumed only when there was no downstream handler
  registered (the data will be discarded in that case) or when
  at least one downstream consumed the data."""
  
  COUNTER = 0
  
  def __init__(
      self, parsing_model, atom_handler_list, event_handler_list,
      max_line_length, default_timestamp_path):
    """Create the atomizer.
    @param event_handler_list when not None, send events to those
    handlers. The list might be empty at invocation and populated
    later on.
    @param max_line_length the maximal line length including the
    final line separator."""
    self.parsing_model = parsing_model
    self.atom_handler_list = atom_handler_list
    self.event_handler_list = event_handler_list
    self.max_line_length = max_line_length
    self.default_timestamp_path = default_timestamp_path

    self.in_overlong_line_flag = False
# If consuming of data was already attempted but the downstream
# handlers refused to handle it, keep the data and the parsed
# object to avoid expensive duplicate parsing operation. The data
# does not include the line separators any more.
    self.last_unconsumed_log_atom = None

  def consume_data(self, stream_data, end_of_stream_flag=False):
    """Consume data from the underlying stream for atomizing.
    @return the number of consumed bytes, 0 if the atomizer would
    need more data for a complete atom or -1 when no data was
    consumed at the moment but data might be consumed later on."""
# Loop until as much streamData as possible was processed and
# then return a result. The correct processing of endOfStreamFlag
# is tricky: by default, even when all data was processed, do
# one more iteration to handle also the flag.
    consumed_length = 0
    while True:
      if self.last_unconsumed_log_atom != None:
# Keep length before dispatching: dispatch will reset the field.
        data_length = len(self.last_unconsumed_log_atom.raw_data)
        if self.dispatch_atom(self.last_unconsumed_log_atom):
          consumed_length += data_length+1
          continue
# Nothing consumed, tell upstream to wait if appropriate.
        if consumed_length == 0:
          consumed_length = -1
        break

      line_end = stream_data.find(b'\n', consumed_length)
      if self.in_overlong_line_flag:
        if line_end < 0:
          consumed_length = len(stream_data)
          if end_of_stream_flag:
            self.dispatch_event('Overlong line terminated by end of stream', stream_data)
            self.in_overlong_line_flag = False
          break
        consumed_length = line_end+1
        self.in_overlong_line_flag = False
        continue

# This is the valid start of a normal/incomplete/overlong line.
      if line_end < 0:
        tail_length = len(stream_data) - consumed_length
        if tail_length > self.max_line_length:
          self.dispatch_event(
              'Start of overlong line detected', stream_data[consumed_length:])
          self.in_overlong_line_flag = True
          consumed_length = len(stream_data)
# Stay in loop to handle also endOfStreamFlag!
          continue
        if end_of_stream_flag and (tail_length != 0):
          self.dispatch_event('Incomplete last line', stream_data[consumed_length:])
          consumed_length = len(stream_data)
        break

# This is at least a complete/overlong line.
      line_length = line_end+1-consumed_length
      if line_length > self.max_line_length:
        self.dispatch_event('Overlong line detected', stream_data[consumed_length:line_end])
        consumed_length = line_end+1
        continue

# This is a normal line.
      line_data = stream_data[consumed_length:line_end]
      log_atom = LogAtom(line_data, None, None, self)
      if self.parsing_model != None:
        match_context = MatchContext(line_data)
        match_element = self.parsing_model.get_match_element('', match_context)
        if (match_element != None) and not match_context.match_data:
          log_atom.parser_match = ParserMatch(match_element)
          if self.default_timestamp_path != None:
            ts_match = log_atom.parser_match.get_match_dictionary().get(self.default_timestamp_path, None)
            if ts_match != None:
              log_atom.set_timestamp(ts_match.match_object)
      if self.dispatch_atom(log_atom):
        consumed_length = line_end+1
        continue
      if consumed_length == 0:
# Downstream did not want the data, so tell upstream to block
# for a while.
        consumed_length = -1
      break
    return consumed_length

  def dispatch_atom(self, log_atom):
    """Dispatch the data using the appropriate handlers. Also clean
    or set lastUnconsumed fields depending on outcome of dispatching."""
    type(self).COUNTER = type(self).COUNTER + 1
    was_consumed_flag = False
    if not self.atom_handler_list:
      was_consumed_flag = True
    else:
      for handler in self.atom_handler_list:
        if handler.receive_atom(log_atom):
          was_consumed_flag = True

    if was_consumed_flag:
      self.last_unconsumed_log_atom = None
    else:
      self.last_unconsumed_log_atom = log_atom
    return was_consumed_flag

  def dispatch_event(self, message, line_data):
    """Dispatch an event with given message and line data to all
    event handlers."""
    if self.event_handler_list is None:
      return
    for handler in self.event_handler_list:
      handler.receive_event(
          'Input.%s' % self.__class__.__name__, message, [line_data],
          None, None, self)
