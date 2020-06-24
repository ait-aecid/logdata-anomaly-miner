"""This module defines an model element for integer number parsing.

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
from aminer.parsing.MatchElement import MatchElement


class DecimalIntegerValueModelElement(ModelElementInterface):
    """This class defines a model to parse integer values with optional signum or padding. If both are present, it is signum has to be
    before the padding characters."""

    SIGN_TYPE_NONE = 'none'
    SIGN_TYPE_OPTIONAL = 'optional'
    SIGN_TYPE_MANDATORY = 'mandatory'

    PAD_TYPE_NONE = 'none'
    PAD_TYPE_ZERO = 'zero'
    PAD_TYPE_BLANK = 'blank'

    def __init__(self, path_id, value_sign_type=SIGN_TYPE_NONE, value_pad_type=PAD_TYPE_NONE):
        self.path_id = path_id
        self.start_characters = None
        if value_sign_type == DecimalIntegerValueModelElement.SIGN_TYPE_NONE:
            self.start_characters = b'0123456789'
        elif value_sign_type == DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL:
            self.start_characters = b'-0123456789'
        elif value_sign_type == DecimalIntegerValueModelElement.SIGN_TYPE_MANDATORY:
            self.start_characters = b'+-'
        else:
            raise Exception('Invalid valueSignType "%s"' % value_sign_type)

        self.pad_characters = b''
        if value_pad_type == DecimalIntegerValueModelElement.PAD_TYPE_NONE:
            pass
        elif value_pad_type == DecimalIntegerValueModelElement.PAD_TYPE_ZERO:
            self.pad_characters = b'0'
        elif value_pad_type == DecimalIntegerValueModelElement.PAD_TYPE_BLANK:
            self.pad_characters = b' '
        else:
            raise Exception('Invalid valuePadType "%s"' % value_sign_type)
        self.value_pad_type = value_pad_type

    def get_child_elements(self):
        """Get all possible child model elements of this element.
        @return empty list as there are no children of this element."""
        return []

    def get_match_element(self, path, match_context):
        """Find the maximum number of bytes forming a integer number according to the parameters specified.
        @return a match when at least one byte being a digit was found"""
        data = match_context.match_data

        allowed_characters = self.start_characters
        if not data or (data[0] not in allowed_characters):
            return None
        match_len = 1

        allowed_characters = self.pad_characters
        for test_byte in data[match_len:]:
            if test_byte not in allowed_characters:
                break
            match_len += 1
        num_start_pos = match_len
        allowed_characters = b'0123456789'
        for test_byte in data[match_len:]:
            if test_byte not in allowed_characters:
                break
            match_len += 1

        if match_len == 1:
            if data[0] not in b'0123456789':
                return None
        elif num_start_pos == match_len:
            return None

        match_string = data[:match_len]
        if self.pad_characters == b' ' and match_string[0] in b'+-':
            match_value = int(match_string.replace(b' ', b'', 1))
        else:
            match_value = int(match_string)
        match_context.update(match_string)
        return MatchElement('%s/%s' % (path, self.path_id), match_string, match_value, None)
