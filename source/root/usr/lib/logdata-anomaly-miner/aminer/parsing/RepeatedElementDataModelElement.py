"""This module defines a model element that repeats a number of times.

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
from aminer.parsing.ModelElementInterface import ModelElementInterface


class RepeatedElementDataModelElement(ModelElementInterface):
    """Objects of this class match on repeats of a given element."""

    def __init__(self, element_id: str, repeated_element: ModelElementInterface, min_repeat: int = 1, max_repeat: int = 0x100000):
        """
        Initialize the ModelElement.
        @param element_id an identifier for the ModelElement which is shown in the path.
        @param repeated_element the MatchElement to be repeated in the data.
        @param min_repeat the minimum number of repeated matches of the repeated_element.
        @param max_repeat the maximum number of repeated matches of the repeated_element.
        """
        super().__init__(element_id, repeated_element=repeated_element, min_repeat=min_repeat, max_repeat=max_repeat)

    def get_match_element(self, path, match_context):
        """Find a suitable number of repeats."""
        current_path = "%s/%s" % (path, self.element_id)

        start_data = match_context.match_data
        matches = []
        match_count = 0
        while match_count != self.max_repeat + 1:
            child_match = self.repeated_element.get_match_element("%s/%s" % (current_path, match_count), match_context)
            if child_match is None:
                break
            matches += [child_match]
            match_count += 1
        if match_count < self.min_repeat or match_count > self.max_repeat:
            match_context.match_data = start_data
            return None

        return MatchElement(current_path, start_data[:len(start_data) - len(match_context.match_data)],
                            start_data[:len(start_data) - len(match_context.match_data)], matches)
