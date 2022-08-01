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

from aminer.parsing.MatchElement import MatchElement
from aminer.parsing.ModelElementInterface import ModelElementInterface


class FixedDataModelElement(ModelElementInterface):
    """
    This class defines a model element of a fixed string.
    The model element is considered a match if the fixed string is found at this position in the log atom.
    """

    def __init__(self, element_id: str, fixed_data: bytes):
        """
        Initialize the ModelElement.
        @param element_id an identifier for the ModelElement which is shown in the path.
        @param fixed_data a non-escaped delimiter string to search for.
        """
        super().__init__(element_id, fixed_data=fixed_data)

    def get_match_element(self, path: str, match_context):
        """@return None when there is no match, MatchElement otherwise."""
        if not match_context.match_data.startswith(self.fixed_data):
            return None
        match_context.update(self.fixed_data)
        return MatchElement("%s/%s" % (path, self.element_id), self.fixed_data, self.fixed_data, None)
