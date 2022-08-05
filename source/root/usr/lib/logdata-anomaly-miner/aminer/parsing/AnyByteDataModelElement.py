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
from aminer.parsing.MatchElement import MatchElement
from aminer.parsing.ModelElementInterface import ModelElementInterface


class AnyByteDataModelElement(ModelElementInterface):
    """This class matches any byte but at least one. Thus, a match will always span the complete data from beginning to end."""

    def get_match_element(self, path: str, match_context):
        """
        Just return a match including all data from the context.
        @param path to be printed in the MatchElement.
        @param match_context the match_context to be analyzed.
        """
        match_data = match_context.match_data
        if not match_data:
            return None
        match_context.update(match_data)
        return MatchElement(f"{path}/{self.element_id}", match_data, match_data, None)
