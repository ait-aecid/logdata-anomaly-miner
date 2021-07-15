"""
This module defines an model element for decimal number parsing as float.

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
from aminer.AminerConfig import DEBUG_LOG_NAME
from aminer.parsing.ModelElementInterface import ModelElementInterface
from aminer.parsing.MatchElement import MatchElement


class DecimalFloatValueModelElement(ModelElementInterface):
    """
    This class defines a model to parse decimal values with optional signum, padding or exponent.
    With padding, the signum has to be found before the padding characters.
    """

    SIGN_TYPE_NONE = "none"
    SIGN_TYPE_OPTIONAL = "optional"
    SIGN_TYPE_MANDATORY = "mandatory"

    PAD_TYPE_NONE = "none"
    PAD_TYPE_ZERO = "zero"
    PAD_TYPE_BLANK = "blank"

    EXP_TYPE_NONE = "none"
    EXP_TYPE_OPTIONAL = "optional"
    EXP_TYPE_MANDATORY = "mandatory"

    def __init__(self, element_id: str, value_sign_type: str = SIGN_TYPE_NONE, value_pad_type: str = PAD_TYPE_NONE,
                 exponent_type: str = EXP_TYPE_NONE):
        if not isinstance(element_id, str):
            msg = "element_id has to be of the type string."
            logging.getLogger(DEBUG_LOG_NAME).error(msg)
            raise TypeError(msg)
        if len(element_id) < 1:
            msg = "element_id must not be empty."
            logging.getLogger(DEBUG_LOG_NAME).error(msg)
            raise ValueError(msg)
        self.element_id = element_id

        if not isinstance(value_sign_type, str):
            msg = 'value_sign_type must be of type string.' % value_sign_type
            logging.getLogger(DEBUG_LOG_NAME).error(msg)
            raise TypeError(msg)
        if value_sign_type == DecimalFloatValueModelElement.SIGN_TYPE_NONE:
            self.start_characters = b"0123456789"
        elif value_sign_type == DecimalFloatValueModelElement.SIGN_TYPE_OPTIONAL:
            self.start_characters = b"-0123456789"
        elif value_sign_type == DecimalFloatValueModelElement.SIGN_TYPE_MANDATORY:
            self.start_characters = b"+-"
        else:
            msg = 'Invalid value_sign_type "%s"' % value_sign_type
            logging.getLogger(DEBUG_LOG_NAME).error(msg)
            raise ValueError(msg)

        self.pad_characters = b""
        if not isinstance(value_pad_type, str):
            msg = 'value_pad_type must be of type string.' % value_sign_type
            logging.getLogger(DEBUG_LOG_NAME).error(msg)
            raise TypeError(msg)
        if value_pad_type == DecimalFloatValueModelElement.PAD_TYPE_NONE:
            pass
        elif value_pad_type == DecimalFloatValueModelElement.PAD_TYPE_ZERO:
            self.pad_characters = b"0"
        elif value_pad_type == DecimalFloatValueModelElement.PAD_TYPE_BLANK:
            self.pad_characters = b" "
        else:
            msg = 'Invalid value_pad_type "%s"' % value_sign_type
            logging.getLogger(DEBUG_LOG_NAME).error(msg)
            raise ValueError(msg)
        self.value_pad_type = value_pad_type

        if not isinstance(exponent_type, str):
            msg = 'exponent_type must be of type string.' % value_sign_type
            logging.getLogger(DEBUG_LOG_NAME).error(msg)
            raise TypeError(msg)
        if exponent_type not in [DecimalFloatValueModelElement.EXP_TYPE_NONE, DecimalFloatValueModelElement.EXP_TYPE_OPTIONAL,
                                 DecimalFloatValueModelElement.EXP_TYPE_MANDATORY]:
            msg = 'Invalid exponent_type "%s"' % exponent_type
            logging.getLogger(DEBUG_LOG_NAME).error(msg)
            raise ValueError(msg)
        self.exponent_type = exponent_type

    def get_id(self):
        """Get the element ID."""
        return self.element_id

    def get_child_elements(self):  # skipcq: PYL-R0201
        """
        Get all possible child model elements of this element.
        @return empty list as there are no children of this element.
        """
        return None

    def get_match_element(self, path: str, match_context):
        """
        Find the maximum number of bytes forming a decimal number according to the parameters specified.
        @return a match when at least one byte being a digit was found
        """
        data = match_context.match_data

        allowed_characters = self.start_characters
        if not data or (data[0] not in allowed_characters):
            return None
        match_len = 1

        if self.pad_characters == b"" and data.startswith(b"0") and not data.startswith(b"0.") and len(data) > 1 and \
                data[1] in b"0123456789":
            return None

        allowed_characters = self.pad_characters
        for test_byte in data[match_len:]:
            if test_byte not in allowed_characters:
                break
            match_len += 1
        num_start_pos = match_len
        allowed_characters = b"0123456789"
        for test_byte in data[match_len:]:
            if test_byte not in allowed_characters:
                break
            match_len += 1

        if match_len == 1:  # skipcq: PTC-W0048
            if data[0] not in b"0123456789":
                return None
        elif num_start_pos == match_len and match_len == 1:  # only return None if match_len is 1 to allow 00 with zero padding.
            return None

        # See if there is decimal part after decimal point.
        if (match_len < len(data)) and (chr(data[match_len]) == "."):
            match_len += 1
            post_point_start = match_len
            for test_byte in data[match_len:]:
                if test_byte not in b"0123456789":
                    break
                match_len += 1
            if match_len == post_point_start - 1:
                # There has to be at least one digit after the decimal point.
                return None

        # See if there could be any exponent following the number.
        if (self.exponent_type != DecimalFloatValueModelElement.EXP_TYPE_NONE) and (match_len + 1 < len(data)) and (
                data[match_len] in b"eE"):
            match_len += 1
            if data[match_len] in b"+-":
                match_len += 1
            exp_number_start = match_len
            for test_byte in data[match_len:]:
                if test_byte not in b"0123456789":
                    break
                match_len += 1
            if match_len == exp_number_start:
                # No exponent number found.
                return None

        match_string = data[:match_len]
        if self.pad_characters == b" " and match_string[0] in b"+-":
            if b" " in match_string.replace(b" ", b"", 1):
                return None
            match_value = float(match_string.replace(b" ", b"", 1))
        else:
            match_value = float(match_string)
        match_context.update(match_string)
        return MatchElement("%s/%s" % (path, self.element_id), match_string, match_value, None)
