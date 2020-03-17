"""This module defines a model element that takes any string
up to the next white space."""

from aminer.parsing.MatchElement import MatchElement
from aminer.parsing import ModelElementInterface

class WhiteSpaceLimitedDataModelElement(ModelElementInterface):
  """This class defines a model element that represents a variable
  amount of characters delimited by a white space."""
  def __init__(self, element_id):
    self.element_id = element_id

  def get_child_elements(self):
    """Get all possible child model elements of this element.
    @return None as there are no children of this element."""
    return None

  def get_match_element(self, path, match_context):
    """Find the maximum number of bytes before encountering whitespace
    or end of data.
    @return a match when at least one byte was found."""
    data = match_context.match_data
    match_len = 0
    for test_byte in data:
      if test_byte in b' \t':
        break
      match_len += 1

    if match_len == 0:
      return None
    match_data = data[:match_len]
    match_context.update(match_data)
    return MatchElement("%s/%s" % (path, self.element_id), match_data, match_data, None)
