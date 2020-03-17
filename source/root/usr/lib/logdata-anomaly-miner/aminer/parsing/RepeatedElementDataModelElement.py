"""This module defines a model element that repeats a number of
times."""

from aminer.parsing.MatchElement import MatchElement
from aminer.parsing import ModelElementInterface

class RepeatedElementDataModelElement(ModelElementInterface):
  """Objects of this class match on repeats of a given element."""
  def __init__(self, elementId, repeatedElement, minRepeat=0, maxRepeat=0x100000, repeatRef=None):
    self.elementId = elementId
    self.repeatedElement = repeatedElement
    self.minRepeat = minRepeat
    self.maxRepeat = maxRepeat

  def get_child_elements(self):
    """Return a list of all children model elements."""
    return [self.repeatedElement]

  def get_match_element(self, path, match_context):
    """Find a suitable number of repeats."""
    currentPath = "%s/%s" % (path, self.elementId)

    startData = match_context.matchData
    matches = []
    matchCount = 0
    while matchCount != self.maxRepeat+1:
      childMatch = self.repeatedElement.get_match_element(
          '%s/%s' % (currentPath, matchCount),
          match_context)
      if childMatch is None:
        break
      matches += [childMatch]
      matchCount += 1
    if matchCount < self.minRepeat or matchCount > self.maxRepeat:
      match_context.matchData = startData
      return None

    return MatchElement(currentPath, \
                        startData[:len(startData)-len(match_context.matchData)],
                        startData[:len(startData)-len(match_context.matchData)], matches)
