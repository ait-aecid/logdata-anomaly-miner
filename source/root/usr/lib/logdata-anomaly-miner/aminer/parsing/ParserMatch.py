"""This module defines a matching parser model element."""

from collections import deque


class ParserMatch:
  """Objects of this class store information about a complete
  model match. Unlike the MatchElement, this class also provides
  fields to store information commonly used when dealing with
  the match."""

  def __init__(self, match_element, parsing_process_data=None):
    """Initialize the match.
    @param match_element the root MatchElement from the parsing
    process.
    @param parsing_process_data this parameter might provide more
    information about the parsing process, e.g. when parsing produced
    warnings. The data is specific for the source producing the
    match."""
    self.match_element = match_element
    self.parsing_process_data = parsing_process_data
    self.match_dictionary = None

  def get_match_element(self):
    """Return the matching element."""
    return self.match_element

  def get_match_dictionary(self):
    """Return a dictionary of all children matches."""
    if self.match_dictionary is not None:
      return self.match_dictionary
    stack = deque()
    stack.append([self.match_element])
    result_dict = {}
    while stack:
      match_list = stack.pop()
      for test_match in match_list:
        result_dict[test_match.path] = test_match
        children = test_match.children
        if (children is not None) and children:
          stack.append(children)
    self.match_dictionary = result_dict
    return result_dict

  def __str__(self):
    return 'ParserMatch: %s' % (self.match_element.annotate_match('  '))
