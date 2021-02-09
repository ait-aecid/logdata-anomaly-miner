"""
This module defines a model element that represents a hex string of arbitrary length.

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


class HexStringModelElement(ModelElementInterface):
    """This class just tries to strip off as many hex bytes as possible from a given data string."""

    def __init__(self, element_id, upper_case=False):
        self.element_id = element_id
        if upper_case:
            self.char_start = ord('A')
        else:
            self.char_start = ord('a')

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
        """
        Find the maximum number of bytes forming a integer number according to the parameters specified.
        @return a match when at least one byte being a digit was found
        """
        data = match_context.match_data
        match_len = 0
        for b_val in data:
            if ((b_val < 0x30) or (b_val > 0x39)) and ((b_val < self.char_start) or (b_val - self.char_start > 5)):
                break
            match_len += 1

        if match_len == 0:
            return None

        match_object = data[:match_len]
        try:
            match_string = bytes.fromhex(match_object.decode())
        except ValueError:
            return None

        match_context.update(match_object)
        return MatchElement("%s/%s" % (path, self.element_id), match_string, match_object, None)
