"""This module defines a model element representing a fixed string."""

from aminer.parsing.MatchElement import MatchElement
from aminer.parsing import ModelElementInterface


class FixedDataModelElement(ModelElementInterface):
    """This class defines a model element of a fixed string. The model element is considered a match if the fixed string is found at
    this position in the log atom."""

    def __init__(self, element_id, fixed_data):
        if not isinstance(fixed_data, bytes):
            raise Exception('fixedData has to be byte string')
        self.element_id = element_id
        self.fixed_data = fixed_data

    def get_child_elements(self):
        """Get all possible child model elements of this element.
        @return None as there are no children of this element."""
        return None

    def get_match_element(self, path, match_context):
        """@return None when there is no match, MatchElement otherwise."""
        if not match_context.match_data.startswith(self.fixed_data):
            return None
        match_context.update(self.fixed_data)
        return MatchElement("%s/%s" % (path, self.element_id), self.fixed_data, self.fixed_data, None)
