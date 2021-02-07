"""
This module provides base64 string matching.

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


import base64

from aminer.parsing.ModelElementInterface import ModelElementInterface
from aminer.parsing.MatchElement import MatchElement


class Base64StringModelElement(ModelElementInterface):
    """This class just tries to strip off as many base64 bytes as possible from a given data string."""

    def __init__(self, path_id):
        self.path_id = path_id

    def get_id(self):
        """Get the element ID."""
        return self.path_id

    def get_child_elements(self):
        """
        Get all possible child model elements of this element.
        @return None as no children are allowed.
        """
        return None

    def get_match_element(self, path, match_context):
        """
        Find the maximum number of bytes forming a integer number according to the parameters specified.
        @return a match when at least one byte being a digit was found.
        """
        data = match_context.match_data
        match_len = 0
        at_end_flag = False
        for test_byte in data:
            b_val = test_byte
            if at_end_flag:
                if ((match_len & 0x3) == 0) or (b_val != 0x3d):
                    break
            elif (not (0x30 <= b_val <= 0x39) and not (0x41 <= b_val <= 0x5a) and not (0x61 <= b_val <= 0x7a) and (
                    b_val not in [0x2b, 0x2f])):
                if (b_val != 0x3d) or ((match_len & 0x2) == 0):
                    break
                at_end_flag = True
            match_len += 1

        match_len = match_len & (-4)
        if match_len == 0:
            return None

        match_string = data[:match_len]
        match_context.update(match_string)
        return MatchElement("%s/%s" % (path, self.path_id), match_string, base64.b64decode(match_string), None)
