"""This module defines various interfaces for log atom parsing and namespace shortcuts to the ModelElements.

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

import abc


class ModelElementInterface(metaclass=abc.ABCMeta):
    """This is the superinterface of all model elements."""

    @abc.abstractmethod
    def get_id(self):
        """Get the element ID."""

    @abc.abstractmethod
    def get_child_elements(self):
        """
        Get all possible child model elements of this element.
        If this element implements a branching model element, then not all child element IDs will be found in matches produced by
        get_match_element.
        @return a list with all children
        """

    @abc.abstractmethod
    def get_match_element(self, path, match_context):
        """
        Try to find a match on given data for this model element and all its children.
        When a match is found, the matchContext is updated accordingly.
        @param path the model path to the parent model element invoking this method.
        @param match_context an instance of MatchContext class holding the data context to match against.
        @return the match_element or None if model did not match.
        """
