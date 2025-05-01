"""This module defines a model element that takes any string up to the next
white space.

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


class WhiteSpaceLimitedDataModelElement(ModelElementInterface):
    """This class defines a model element that represents a variable amount of
    characters delimited by a white space."""

    def get_match_element(self, path: str, match_context):
        """Find the maximum number of bytes before encountering whitespace or
        end of data.

        @return a match when at least one byte was found.
        """
        data = match_context.match_data
        match_len = 0
        for test_byte in data:
            if test_byte in b" \t":
                break
            match_len += 1

        if match_len == 0:
            return None
        match_data = data[:match_len]
        match_context.update(match_data)
        return MatchElement(f"{path}/{self.element_id}", match_data, match_data, None)
