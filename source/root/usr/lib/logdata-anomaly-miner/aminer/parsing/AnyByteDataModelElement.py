"""This module defines a model element that matches any byte."""

from aminer.parsing.MatchElement import MatchElement

class AnyByteDataModelElement:
  """This class matches any byte but at least one. Thus a match
  will always span the complete data from beginning to end."""
  def __init__(self, elementId):
    self.elementId = elementId

  def getChildElements(self):
    """Get all possible child model elements of this element.
    @return None as there are no children of this element."""
    return None

  def getMatchElement(self, path, matchContext):
    """Just return a match including all data from the context"""
    matchData = matchContext.matchData
    if not matchData:
      return None
    matchContext.update(matchData)
    return MatchElement("%s/%s" % (path, self.elementId), \
        matchData, matchData, None)
