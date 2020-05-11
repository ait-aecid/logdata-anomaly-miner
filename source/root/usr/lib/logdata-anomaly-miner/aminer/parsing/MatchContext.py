"""This module defines the match context."""

from aminer.parsing.MatchElement import MatchElement


class MatchContext(object):
  """This class allows storage of data relevant during the matching
  process, e.g. the root node and the remaining unmatched data.
  Then searching for non-atomic matches, e.g. sequences, the context
  might be modified by model subelements, even if the main model
  element will not return a match. In that case, those non-atomic
  model elements have to care to restore the context before returning."""

  def __init__(self, match_data):
    """Create a MatchContext with the full unmatched string data.
    @param match_data the data that will be tested by the next
    model element."""
    self.match_data = match_data
    self.root_match_element = MatchElement('/', None, None, [])

  def update(self, match_string):
    """Update the match context by removing the given matched
    string data from the context data still to be matched. This
    method does not check, if the removed data is the same as
    the trailing match data for performance reasons. This is done
    only in the DebugMatchContext class."""
    self.match_data = self.match_data[len(match_string):]


class DebugMatchContext(MatchContext):
  """This class defines a slower MatchContext for debugging purposes."""

  def __init__(self, match_data):
    self.debug_info = ''
    self.last_match_data = None
    self.shortest_unmatched_data = match_data
    super(DebugMatchContext, self).__init__(match_data)

  def update(self, match_string):
    """Update the context and store debugging information."""
    if self.last_match_data != self.match_data:
      self.last_match_data = self.match_data
      if self.debug_info != '':
        self.debug_info += '  '
      self.debug_info += 'Starting match update on %s\n' % repr(self.match_data)
    if not self.match_data.startswith(match_string):
      self.debug_info += '  Current data %s does not start with %s\n' % (
        repr(self.match_data), repr(match_string))
      raise Exception('Illegal state')
    self.match_data = self.match_data[len(match_string):]
    self.last_match_data = self.match_data
    if (self.shortest_unmatched_data is None) or (
            len(self.match_data) < len(self.shortest_unmatched_data)):
      self.shortest_unmatched_data = self.match_data
    self.debug_info += '  Removed %s, remaining %d bytes\n' % (repr(match_string), len(self.match_data))

  def get_debug_info(self):
    """Get the current debugging information and reset it."""
    while self.debug_info.find('\n\n') != -1:
      self.debug_info = self.debug_info.replace('\n\n', '\n')
    result = self.debug_info
    self.debug_info = ''
    result += '  Shortest unmatched data was %s\n' % repr(self.shortest_unmatched_data)
    return result

  def getshortest_unmatched_data(self):
    """Get shortest match_data found while updating the internal
    state. This is useful to find out where the parsing process
    has terminated."""
    return self.shortest_unmatched_data
