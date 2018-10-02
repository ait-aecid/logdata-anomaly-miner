"""This module defines a model element for a variable amount of
bytes."""

from aminer.parsing.MatchElement import MatchElement

class VariableByteDataModelElement:
  """This class defines a model element  that takes any string that
  only contains characters of a given alphabet."""
  def __init__(self, elementId, alphabet):
    self.elementId = elementId
    self.alphabet = alphabet

  def getChildElements(self):
    """Get all possible child model elements of this element.
    @return None as there are no children of this element."""
    return None

  def getMatchElement(self, path, matchContext):
    """Find the maximum number of bytes matching the given alphabet.
    @return a match when at least one byte was found within alphabet."""
    data = matchContext.matchData
    matchLen = 0
    for testByte in data:
      if testByte not in self.alphabet:
        break
      matchLen += 1

    if matchLen == 0:
      return None
    matchData = data[:matchLen]
    matchContext.update(matchData)
    return MatchElement("%s/%s" % (path, self.elementId), matchData, matchData, None)
