"""
This module defines a model element that matches any byte.

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
import logging
import typic
from aminer import AminerConfig
from aminer.parsing.MatchElement import MatchElement
from aminer.parsing.ModelElementInterface import ModelElementInterface


class AnyByteDataModelElement(ModelElementInterface):
    """This class matches any byte but at least one. Thus a match will always span the complete data from beginning to end."""

    @typic.al(strict=True)
    def __init__(self, element_id: str):
        if len(element_id) < 1:
            msg = "element_id must not be empty."
            logging.getLogger(AminerConfig.DEBUG_LOG_NAME).error(msg)
            raise typic.constraints.error.ConstraintValueError(msg)
        self.element_id = element_id

    def get_id(self):
        """Get the element ID."""
        return self.element_id

    def get_child_elements(self):  # skipcq: PYL-R0201
        """
        Get all possible child model elements of this element.
        @return None as there are no children of this element.
        """
        return None

    @typic.al(strict=True)
    def get_match_element(self, path: str, match_context):
        """Just return a match including all data from the context."""
        match_data = match_context.match_data
        if not match_data:
            return None
        match_context.update(match_data)
        return MatchElement("%s/%s" % (path, self.element_id), match_data, match_data, None)
