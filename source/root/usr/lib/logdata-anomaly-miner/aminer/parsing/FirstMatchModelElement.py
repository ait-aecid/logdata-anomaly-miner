"""This module defines a model element that allows branches. The
first matching branch is taken."""

from aminer.parsing import ModelElementInterface


class FirstMatchModelElement(ModelElementInterface):
  """This class defines a model element to return the match from
  the the first matching child model within a given list."""
  def __init__(self, element_id, children):
    self.element_id = element_id
    self.children = children
    if (children is None) or (None in children):
      raise Exception('Invalid children list')

  def get_child_elements(self):
    """Get all possible child model elements of this element."""
    return self.children

  def get_match_element(self, path, match_context):
    """@return None when there is no match, MatchElement otherwise."""
    current_path = "%s/%s" % (path, self.element_id)

    match_data = match_context.match_data
    for child_element in self.children:
      child_match = child_element.get_match_element(current_path, match_context)
      if child_match is not None:
        return child_match
      match_context.match_data = match_data
    return None
