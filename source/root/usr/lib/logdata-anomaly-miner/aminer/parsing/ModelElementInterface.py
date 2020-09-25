"""This module defines various interfaces for log atom parsing
and namespace shortcuts to the ModelElements."""


class ModelElementInterface:
    """This is the superinterface of all model elements."""

    # skipcq: PYL-R0201
    def get_id(self):
        """Get the element ID."""
        raise Exception('Interface method called')

    # skipcq: PYL-R0201
    def get_child_elements(self):
        """Get all possible child model elements of this element. If this element implements a branching model element, then
        not all child element IDs will be found in matches produced by getMatchElement.
        @return a list with all children"""
        raise Exception('Interface method called')

    def get_match_element(self, path, match_context):
        """Try to find a match on given data for this model element and all its children. When a match is found, the matchContext
        is updated accordingly.
        @param path the model path to the parent model element invoking this method.
        @param match_context an instance of MatchContext class holding the data context to match against.
        @return the match_element or None if model did not match."""
