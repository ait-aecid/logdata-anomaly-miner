"""This module defines a model element that consists of a sequence of model elements that all have to match.

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.
This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with
this program. If not, see <http://www.gnu.org/licenses/>.
"""

from aminer.parsing.MatchElement import MatchElement
from aminer.parsing import ModelElementInterface


class SequenceModelElement(ModelElementInterface):
    """This class defines an element to find matches that comprise matches of all given child model elements."""

    def __init__(self, element_id, children):
        self.element_id = element_id
        self.children = children

    def get_child_elements(self):
        """Return all model elements of the sequence."""
        return self.children

    def get_match_element(self, path, match_context):
        """Try to find a match on given data for this model element and all its children. When a match is found, the matchContext
        is updated accordingly.
        @param path the model path to the parent model element invoking this method.
        @param match_context an instance of MatchContext class holding the data context to match against.
        @return the matchElement or None if model did not match."""
        current_path = "%s/%s" % (path, self.element_id)
        start_data = match_context.match_data
        matches = []
        for child_element in self.children:
            child_match = child_element.get_match_element(current_path, match_context)
            if child_match is None:
                match_context.match_data = start_data
                return None
            matches += [child_match]

        return MatchElement(current_path, start_data[:len(start_data) - len(match_context.match_data)],
                            start_data[:len(start_data) - len(match_context.match_data)], matches)
