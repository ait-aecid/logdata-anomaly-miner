"""This module defines a model element that allows branches. The
first matching branch is taken."""

from aminer.parsing import ModelElementInterface

class FirstMatchModelElement(ModelElementInterface):
  """This class defines a model element to return the match from
  the the first matching child model within a given list."""
  def __init__(self, elementId, children):
    self.elementId = elementId
    self.children = children
    if (children is None) or (None in children):
      raise Exception('Invalid children list')

  def get_child_elements(self):
    """Get all possible child model elements of this element."""
    return self.children

  def get_match_element(self, path, matchContext):
    """@return None when there is no match, MatchElement otherwise."""
    currentPath = "%s/%s" % (path, self.elementId)

    matchData = matchContext.matchData
    for childElement in self.children:
      childMatch = childElement.get_match_element(currentPath, matchContext)
      if childMatch != None:
        return childMatch
      matchContext.matchData = matchData
    return None
