"""This module defines a model element that is optional."""

from aminer.parsing.MatchElement import MatchElement
from aminer.parsing import ModelElementInterface

class OptionalMatchModelElement(ModelElementInterface):
  """This class defines a model element tries to match against
  a given model element and if that fails returns a zero length
  match anyway."""
  def __init__(self, elementId, optionalElement):
    self.elementId = elementId
    self.optionalElement = optionalElement

  def getChildElements(self):
    """Return all optional elements."""
    return [self.optionalElement]

  def getMatchElement(self, path, matchContext):
    """@return the embedded child match or an empty match."""
    currentPath = "%s/%s" % (path, self.elementId)

    startData = matchContext.matchData
    match = self.optionalElement.getMatchElement(currentPath, matchContext)
    if match is None:
      return MatchElement("%s/%s" % (path, self.elementId), \
          '', None, None)

    return MatchElement(currentPath, \
        startData[:len(startData)-len(matchContext.matchData)], 
        startData[:len(startData)-len(matchContext.matchData)], [match])
