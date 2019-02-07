"""This module defines a model element that takes any string
up to the next white space."""

from aminer.parsing.MatchElement import MatchElement
from aminer.parsing import ModelElementInterface

class WhiteSpaceLimitedDataModelElement(ModelElementInterface):
  """This class defines a model element that represents a variable
  amount of characters delimited by a white space."""
  def __init__(self, elementId):
    self.elementId = elementId

  def getChildElements(self):
    """Get all possible child model elements of this element.
    @return None as there are no children of this element."""
    return None

  def getMatchElement(self, path, matchContext):
    """Find the maximum number of bytes before encountering whitespace
    or end of data.
    @return a match when at least one byte was found."""
    data = matchContext.matchData
    matchLen = 0
    for testByte in data:
      if testByte in b' \t':
        break
      matchLen += 1

    if matchLen == 0:
      return None
    matchData = data[:matchLen]
    matchContext.update(matchData)
    return MatchElement("%s/%s" % (path, self.elementId), matchData, matchData, None)
