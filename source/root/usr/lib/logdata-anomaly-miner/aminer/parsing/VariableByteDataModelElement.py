"""This module defines a model element for a variable amount of
bytes."""

from aminer.parsing.MatchElement import MatchElement
from aminer.parsing import ModelElementInterface

class VariableByteDataModelElement(ModelElementInterface):
  """This class defines a model element  that takes any string that
  only contains characters of a given alphabet."""
  def __init__(self, element_id, alphabet):
    self.element_id = element_id
    self.alphabet = alphabet

  def get_child_elements(self):
    """Get all possible child model elements of this element.
    @return None as there are no children of this element."""
    return None

  def get_match_element(self, path, match_context):
    """Find the maximum number of bytes matching the given alphabet.
    @return a match when at least one byte was found within alphabet."""
    data = match_context.matchData
    match_len = 0
    for test_byte in data:
      if test_byte not in self.alphabet:
        break
      match_len += 1

    if match_len == 0:
      return None
    match_data = data[:match_len]
    match_context.update(match_data)
    return MatchElement("%s/%s" % (path, self.element_id), match_data, match_data, None)
