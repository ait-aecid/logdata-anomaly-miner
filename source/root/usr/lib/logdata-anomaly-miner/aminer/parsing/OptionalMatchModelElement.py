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

  def get_child_elements(self):
    """Return all optional elements."""
    return [self.optionalElement]

  def get_match_element(self, path, match_context):
    """@return the embedded child match or an empty match."""
    currentPath = "%s/%s" % (path, self.elementId)

    startData = match_context.matchData
    match = self.optionalElement.get_match_element(currentPath, match_context)
    if match is None:
      return MatchElement("%s/%s" % (path, self.elementId), \
          '', None, None)

    return MatchElement(currentPath, \
                        startData[:len(startData)-len(match_context.matchData)],
                        startData[:len(startData)-len(match_context.matchData)], [match])
