"""This module defines the match context."""

from aminer.parsing.MatchElement import MatchElement

class MatchContext(object):
  """This class allows storage of data relevant during the matching
  process, e.g. the root node and the remaining unmatched data.
  Then searching for non-atomic matches, e.g. sequences, the context
  might be modified by model subelements, even if the main model
  element will not return a match. In that case, those non-atomic
  model elements have to care to restore the context before returning."""

  def __init__(self, matchData):
    """Create a MatchContext with the full unmatched string data.
    @param matchData the data that will be tested by the next
    model element."""
    self.matchData = matchData
    self.rootMatchElement = MatchElement('/', None, None, [])

  def update(self, matchString):
    """Update the match context by removing the given matched
    string data from the context data still to be matched. This
    method does not check, if the removed data is the same as
    the trailing match data for performance reasons. This is done
    only in the DebugMatchContext class."""
    self.matchData = self.matchData[len(matchString):]


class DebugMatchContext(MatchContext):
  """This class defines a slower MatchContext for debugging purposes."""

  def __init__(self, matchData):
    self.debugInfo = ''
    self.lastMatchData = None
    self.shortestUnmatchedData = None
    super(DebugMatchContext, self).__init__(matchData)

  def update(self, matchString):
    """Update the context and store debugging information."""
    if self.lastMatchData != self.matchData:
      self.lastMatchData = self.matchData
      self.debugInfo += 'Starting match update on %s\n' % repr(self.matchData)
    if not self.matchData.startswith(matchString):
      self.debugInfo += 'Current data %s does not start with %s\n' % (
          repr(self.matchData), repr(matchString))
      raise Exception('Illegal state')
    self.matchData = self.matchData[len(matchString):]
    self.lastMatchData = self.matchData
    if (self.shortestUnmatchedData is None) or (
        len(self.matchData) < len(self.shortestUnmatchedData)):
      self.shortestUnmatchedData = self.matchData
    self.debugInfo += 'Removed %s, remaining %d bytes\n' % (repr(matchString), len(self.matchData))

  def getDebugInfo(self):
    """Get the current debugging information and reset it."""
    result = self.debugInfo
    self.debugInfo = ''
    result += 'Shortest unmatched data was %s\n' % repr(self.shortestUnmatchedData)
    return result

  def getshortestUnmatchedData(self):
    """Get shortest matchData found while updating the internal
    state. This is useful to find out where the parsing process
    has terminated."""
    return self.shortestUnmatchedData
