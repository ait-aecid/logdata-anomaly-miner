"""This module defines a model element that consists of a sequence
of model elements that all have to match."""

from aminer.parsing.MatchElement import MatchElement
from aminer.parsing import ModelElementInterface

class SequenceModelElement(ModelElementInterface):
  """This class defines an element to find matches that comprise
  matches of all given child model elements."""
  def __init__(self, elementId, children):
    self.elementId = elementId
    self.children = children

  def get_child_elements(self):
    """Return all model elements of the sequence."""
    return self.children

  def get_match_element(self, path, match_context):
    """Try to find a match on given data for this model element
    and all its children. When a match is found, the matchContext
    is updated accordingly.
    @param path the model path to the parent model element invoking
    this method.
    @param match_context an instance of MatchContext class holding
    the data context to match against.
    @return the matchElement or None if model did not match."""
    currentPath = "%s/%s" % (path, self.elementId)
    startData = match_context.matchData
    matches = []
    for childElement in self.children:
      childMatch = childElement.get_match_element(currentPath, match_context)
      if childMatch is None:
        match_context.matchData = startData
        return None
      matches += [childMatch]

    return MatchElement(currentPath, \
                        startData[:len(startData)-len(match_context.matchData)],
                        startData[:len(startData)-len(match_context.matchData)], matches)
