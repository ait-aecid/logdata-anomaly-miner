"""This module defines a model element that represents a hex string
of arbitrary length."""

from aminer.parsing.MatchElement import MatchElement
from aminer.parsing import ModelElementInterface

class HexStringModelElement(ModelElementInterface):
  """This class just tries to strip off as many hex bytes as possible
  from a given data string."""
  def __init__(self, element_id, upper_case=False):
    self.element_id = element_id
    if upper_case:
      self.char_start = ord('A')
    else:
      self.char_start = ord('a')

  def get_child_elements(self):
    """Get all possible child model elements of this element.
    @return None as there are no children of this element."""
    return None

  def get_match_element(self, path, match_context):
    """Find the maximum number of bytes forming a integer number
    according to the parameters specified
    @return a match when at least one byte being a digit was found"""
    data = match_context.match_data
    match_len = 0
    for b_val in data:
      if ((b_val < 0x30) or (b_val > 0x39)) and ((b_val < self.char_start) or (
              b_val - self.char_start > 5)):
        break
      match_len += 1

    if match_len == 0:
      return None

    match_object = data[:match_len]
    try:
      match_string = bytes.fromhex(match_object.decode('utf-8'))
    except ValueError:
      return None
    
    match_context.update(match_object)
    return MatchElement("%s/%s" % (path, self.element_id), \
                        match_string, match_object, None)
