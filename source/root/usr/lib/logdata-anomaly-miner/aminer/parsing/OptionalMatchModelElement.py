"""This module defines a model element that is optional."""

from aminer.parsing.MatchElement import MatchElement
from aminer.parsing import ModelElementInterface


class OptionalMatchModelElement(ModelElementInterface):
  """This class defines a model element tries to match against
  a given model element and if that fails returns a zero length
  match anyway."""
  def __init__(self, element_id, optional_element):
    self.element_id = element_id
    self.optional_element = optional_element

  def get_child_elements(self):
    """Return all optional elements."""
    return [self.optional_element]

  def get_match_element(self, path, match_context):
    """@return the embedded child match or an empty match."""
    current_path = "%s/%s" % (path, self.element_id)

    start_data = match_context.match_data
    match = self.optional_element.get_match_element(current_path, match_context)
    if match is None:
      return MatchElement("%s/%s" % (path, self.element_id), \
          '', None, None)

    return MatchElement(current_path, \
                        start_data[:len(start_data)-len(match_context.match_data)],
                        start_data[:len(start_data)-len(match_context.match_data)], [match])
