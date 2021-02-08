"""
This module defines a model element representing a fixed string.

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
from aminer import AminerConfig
from aminer.parsing.MatchElement import MatchElement
from aminer.parsing.ModelElementInterface import ModelElementInterface


class FixedDataModelElement(ModelElementInterface):
    """
    This class defines a model element of a fixed string.
    The model element is considered a match if the fixed string is found at this position in the log atom.
    """

    def __init__(self, element_id, fixed_data):
        if not isinstance(fixed_data, bytes):
            msg = 'fixedData has to be byte string'
            logging.getLogger(AminerConfig.DEBUG_LOG_NAME).error(msg)
            raise Exception(msg)
        self.element_id = element_id
        self.fixed_data = fixed_data

    def get_id(self):
        """Get the element ID."""
        return self.element_id

    def get_child_elements(self):
        """
        Get all possible child model elements of this element.
        @return None as there are no children of this element.
        """
        return None

    def get_match_element(self, path, match_context):
        """@return None when there is no match, MatchElement otherwise."""
        if not match_context.match_data.startswith(self.fixed_data):
            return None
        match_context.update(self.fixed_data)
        return MatchElement("%s/%s" % (path, self.element_id), self.fixed_data, self.fixed_data, None)
