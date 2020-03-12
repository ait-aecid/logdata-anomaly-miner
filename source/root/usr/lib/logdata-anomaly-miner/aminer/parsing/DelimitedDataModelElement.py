"""This module defines a model element that takes any string up
to a specific delimiter string."""

from aminer.parsing.MatchElement import MatchElement
from aminer.parsing import ModelElementInterface
import re

class DelimitedDataModelElement(ModelElementInterface):
  """Find a string delimited by given non-escaped delimiter string,
  possibly a match of zero byte length"""
  def __init__(self, elementId, delimiter, escape=None):
    self.elementId = elementId
    self.delimiter = delimiter
    self.escape = escape

  def getChildElements(self):
    """Get all possible child model elements of this element.
    @return None as there are no children of this element."""
    return None

  def getMatchElement(self, path, matchContext):
    """Find the maximum number of bytes before encountering the
    non-escaped delimiter.
    @return a match when at least one byte was found but not the
    delimiter itself."""
    data = matchContext.matchData
    if self.escape is None:
      matchLen = re.search(self.delimiter, data).start()
    else:
      matchLen = re.search(rb'(?<!' + re.escape(self.escape) + rb')' + self.delimiter, data).start()
    if matchLen < 1:
      return None
    matchData = data[:matchLen]
    matchContext.update(matchData)
    return MatchElement("%s/%s" % (path, self.elementId), \
        matchData, matchData, None)
