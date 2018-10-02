"""This module defines a model element that takes any string up
to a specific delimiter string."""

from aminer.parsing.MatchElement import MatchElement

class DelimitedDataModelElement:
  """Find a string delimited by given delimiter string, possibly
  a match of zero byte length"""
  def __init__(self, elementId, delimiter):
    self.elementId = elementId
    self.delimiter = delimiter

  def getChildElements(self):
    """Get all possible child model elements of this element.
    @return None as there are no children of this element."""
    return None

  def getMatchElement(self, path, matchContext):
    """Find the maximum number of bytes before encountering the
    delimiter.
    @return a match when at least one byte was found but not the
    delimiter itself."""
    data = matchContext.matchData
    matchLen = data.find(self.delimiter)
    if matchLen < 0:
      return None
    matchData = data[:matchLen]
    matchContext.update(matchData)
    return MatchElement("%s/%s" % (path, self.elementId), \
        matchData, matchData, None)
