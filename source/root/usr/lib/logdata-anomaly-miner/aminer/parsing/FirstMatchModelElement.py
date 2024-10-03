"""This module defines a model element that allows branches. The first matching
branch is taken.

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

from aminer.parsing.ModelElementInterface import ModelElementInterface


class FirstMatchModelElement(ModelElementInterface):
    """This class defines a model element to return the match from the the
    first matching child model within a given list."""

    def __init__(self, element_id: str, children: list):
        """Initialize the ModelElement.

        @param element_id an identifier for the ModelElement which is shown in the path.
        @param children a list of child elements to be iterated through.
        """
        super().__init__(element_id, children=children)

    def get_match_element(self, path: str, match_context):
        """@return None when there is no match, MatchElement otherwise."""
        current_path = f"{path}/{self.element_id}"

        match_data = match_context.match_data
        for child_element in self.children:
            child_match = child_element.get_match_element(current_path, match_context)
            if child_match is not None:
                return child_match
            match_context.match_data = match_data
        return None
