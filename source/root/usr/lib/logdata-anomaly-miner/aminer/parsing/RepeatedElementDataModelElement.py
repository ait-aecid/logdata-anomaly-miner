"""This module defines a model element that repeats a number of times."""

from aminer.parsing.MatchElement import MatchElement
from aminer.parsing import ModelElementInterface


class RepeatedElementDataModelElement(ModelElementInterface):
    """Objects of this class match on repeats of a given element."""

    def __init__(self, element_id, repeated_element, min_repeat=0, max_repeat=0x100000):
        self.element_id = element_id
        self.repeated_element = repeated_element
        self.min_repeat = min_repeat
        self.max_repeat = max_repeat

    def get_child_elements(self):
        """Return a list of all children model elements."""
        return [self.repeated_element]

    def get_match_element(self, path, match_context):
        """Find a suitable number of repeats."""
        current_path = "%s/%s" % (path, self.element_id)

        start_data = match_context.match_data
        matches = []
        match_count = 0
        while match_count != self.max_repeat + 1:
            child_match = self.repeated_element.get_match_element('%s/%s' % (current_path, match_count), match_context)
            if child_match is None:
                break
            matches += [child_match]
            match_count += 1
        if match_count < self.min_repeat or match_count > self.max_repeat:
            match_context.match_data = start_data
            return None

        return MatchElement(current_path, start_data[:len(start_data) - len(match_context.match_data)],
                            start_data[:len(start_data) - len(match_context.match_data)], matches)
