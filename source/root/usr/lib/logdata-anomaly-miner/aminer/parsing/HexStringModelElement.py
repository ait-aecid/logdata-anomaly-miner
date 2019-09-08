"""This module defines a model element that represents a hex string
of arbitrary length."""

from aminer.parsing.MatchElement import MatchElement
from aminer.parsing import ModelElementInterface

class HexStringModelElement(ModelElementInterface):
  """This class just tries to strip off as many hex bytes as possible
  from a given data string."""
  def __init__(self, elementId, upperCase=False):
    self.elementId = elementId
    if upperCase:
      self.charStart = ord('A')
    else:
      self.charStart = ord('a')

  def getChildElements(self):
    """Get all possible child model elements of this element.
    @return None as there are no children of this element."""
    return None

  def getMatchElement(self, path, matchContext):
    """Find the maximum number of bytes forming a integer number
    according to the parameters specified
    @return a match when at least one byte being a digit was found"""
    data = matchContext.matchData
    matchLen = 0
    for bVal in data:
      if ((bVal < 0x30) or (bVal > 0x39)) and ((bVal < self.charStart) or (
          bVal-self.charStart > 5)):
        break
      matchLen += 1

    if matchLen == 0:
      return None

    matchString = data[:matchLen]
    matchContext.update(matchString)
    return MatchElement("%s/%s" % (path, self.elementId), \
        bytes.fromhex(matchString.decode('utf-8')), matchString, None)
