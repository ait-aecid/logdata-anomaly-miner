"""This module defines a model element that matches any byte."""

from aminer.parsing.MatchElement import MatchElement
from aminer.parsing import ModelElementInterface


class AnyByteDataModelElement(ModelElementInterface):
  """This class matches any byte but at least one. Thus a match
  will always span the complete data from beginning to end."""
  def __init__(self, element_id):
    self.element_id = element_id

  def get_child_elements(self):
    """Get all possible child model elements of this element.
    @return None as there are no children of this element."""
    return None

  def get_match_element(self, path, match_context):
    """Just return a match including all data from the context"""
    match_data = match_context.match_data
    if not match_data:
      return None
    match_context.update(match_data)
    return MatchElement("%s/%s" % (path, self.element_id), match_data, match_data, None)
