"""This module defines a model element that takes any string up
to a specific delimiter string."""

from aminer.parsing.MatchElement import MatchElement
from aminer.parsing import ModelElementInterface
import re


class DelimitedDataModelElement(ModelElementInterface):
  """Find a string delimited by given non-escaped delimiter string,
  possibly a match of zero byte length"""
  def __init__(self, element_id, delimiter, escape=None):
    self.element_id = element_id
    self.delimiter = delimiter
    self.escape = escape

  def get_child_elements(self):
    """Get all possible child model elements of this element.
    @return None as there are no children of this element."""
    return None

  def get_match_element(self, path, match_context):
    """Find the maximum number of bytes before encountering the
    non-escaped delimiter.
    @return a match when at least one byte was found but not the
    delimiter itself."""
    data = match_context.matchData
    match_len = -1
    if self.escape is None:
      search = re.search(re.escape(self.delimiter), data)
      if search is not None:
        match_len = search.start()
    else:
      search = re.search(rb'(?<!' + re.escape(self.escape) + rb')' + re.escape(self.delimiter), data)
      if search is not None:
        match_len = search.start()
    if match_len < 1:
      return None
    match_data = data[:match_len]
    match_context.update(match_data)
    return MatchElement("%s/%s" % (path, self.element_id), \
                        match_data, match_data, None)
