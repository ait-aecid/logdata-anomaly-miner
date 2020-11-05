"""This module defines a model element that allows branches. The first matching branch is taken.

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


from aminer.parsing import ModelElementInterface


class FirstMatchModelElement(ModelElementInterface):
    """This class defines a model element to return the match from the the first matching child model within a given list."""

    def __init__(self, element_id, children):
        self.element_id = element_id
        self.children = children
        if (children is None) or (None in children):
            raise Exception('Invalid children list')

    def get_id(self):
        """Get the element ID."""
        return self.element_id

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
