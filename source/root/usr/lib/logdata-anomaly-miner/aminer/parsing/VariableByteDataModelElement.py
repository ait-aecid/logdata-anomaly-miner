"""This module defines a model element for a variable amount of
bytes."""

from aminer.parsing.MatchElement import MatchElement
from aminer.parsing import ModelElementInterface

class VariableByteDataModelElement(ModelElementInterface):
  """This class defines a model element  that takes any string that
  only contains characters of a given alphabet."""
  def __init__(self, elementId, alphabet):
    self.elementId = elementId
    self.alphabet = alphabet

  def get_child_elements(self):
    """Get all possible child model elements of this element.
    @return None as there are no children of this element."""
    return None

  def get_match_element(self, path, match_context):
    """Find the maximum number of bytes matching the given alphabet.
    @return a match when at least one byte was found within alphabet."""
    data = match_context.matchData
    matchLen = 0
    for testByte in data:
      if testByte not in self.alphabet:
        break
      matchLen += 1

    if matchLen == 0:
      return None
    matchData = data[:matchLen]
    match_context.update(matchData)
    return MatchElement("%s/%s" % (path, self.elementId), matchData, matchData, None)
