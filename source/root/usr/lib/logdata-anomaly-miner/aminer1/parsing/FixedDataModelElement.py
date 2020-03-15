"""This module defines a model element representing a fixed string."""

from aminer.parsing.MatchElement import MatchElement
from aminer.parsing import ModelElementInterface

class FixedDataModelElement(ModelElementInterface):
  """This class defines a model element of a fixed string. The model
  element is considered a match if the fixed string is found at
  this position in the log atom."""
  def __init__(self, elementId, fixedData):
    if not isinstance(fixedData, bytes):
      raise Exception('fixedData has to be byte string')
    self.elementId = elementId
    self.fixedData = fixedData

  def getChildElements(self):
    """Get all possible child model elements of this element.
    @return None as there are no children of this element."""
    return None

  def getMatchElement(self, path, matchContext):
    """@return None when there is no match, MatchElement otherwise."""
    if not matchContext.matchData.startswith(self.fixedData):
      return None
    matchContext.update(self.fixedData)
    return MatchElement("%s/%s" % (path, self.elementId), \
        self.fixedData, self.fixedData, None)
