"""
This module defines an model element for integer number parsing.

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


class DecimalIntegerValueModelElement(ModelElementInterface):
    """
    This class defines a model to parse integer values with optional signum or padding.
    If both are present, it is signum has to be before the padding characters.
    """

    SIGN_TYPE_NONE = "none"
    SIGN_TYPE_OPTIONAL = "optional"
    SIGN_TYPE_MANDATORY = "mandatory"

    PAD_TYPE_NONE = "none"
    PAD_TYPE_ZERO = "zero"
    PAD_TYPE_BLANK = "blank"

    def __init__(self, element_id: str, value_sign_type: str = SIGN_TYPE_NONE, value_pad_type: str = PAD_TYPE_NONE):
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
            msg = "value_sign_type must be of type string." % value_sign_type
            logging.getLogger(DEBUG_LOG_NAME).error(msg)
            raise TypeError(msg)
        if value_sign_type == DecimalIntegerValueModelElement.SIGN_TYPE_NONE:
            self.start_characters = set(b"0123456789")
        elif value_sign_type == DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL:
            self.start_characters = set(b"-0123456789")
        elif value_sign_type == DecimalIntegerValueModelElement.SIGN_TYPE_MANDATORY:
            self.start_characters = set(b"+-")
        else:
            msg = "Invalid value_sign_type '%s'" % value_sign_type
            logging.getLogger(DEBUG_LOG_NAME).error(msg)
            raise ValueError(msg)

        self.pad_characters = b""
        if not isinstance(value_pad_type, str):
            msg = "value_pad_type must be of type string." % value_sign_type
            logging.getLogger(DEBUG_LOG_NAME).error(msg)
            raise TypeError(msg)
        if value_pad_type == DecimalIntegerValueModelElement.PAD_TYPE_NONE:
            pass
        elif value_pad_type == DecimalIntegerValueModelElement.PAD_TYPE_ZERO:
            self.pad_characters = b"0"
        elif value_pad_type == DecimalIntegerValueModelElement.PAD_TYPE_BLANK:
            self.pad_characters = b" "
        else:
            msg = "Invalid value_pad_type '%s'" % value_sign_type
            logging.getLogger(DEBUG_LOG_NAME).error(msg)
            raise ValueError(msg)
        self.value_pad_type = value_pad_type
        self.digits = set(b"0123456789")

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
        Find the maximum number of bytes forming a integer number according to the parameters specified.
        @return a match when at least one byte being a digit was found.
        """
        data = match_context.match_data

        if not data or (data[0] not in self.start_characters):
            return None
        match_len = 1

        if self.pad_characters == b"" and data.startswith(b"0") and not data.startswith(b"0.") and len(data) > 1 and \
                data[1] in self.digits:
            return None

        for test_byte in data[match_len:]:
            if test_byte not in self.pad_characters:
                break
            match_len += 1
        num_start_pos = match_len
        for test_byte in data[match_len:]:
            if test_byte not in self.digits:
                break
            match_len += 1

        if match_len == 1:  # skipcq: PTC-W0048
            if data[0] not in self.digits:
                return None
        elif num_start_pos == match_len and match_len == 1:  # only return None if match_len is 1 to allow 00 with zero padding.
            return None

        match_string = data[:match_len]
        try:
            if self.pad_characters == b" " and match_string[0] in b"+-":
                match_value = int(match_string.replace(b" ", b"", 1))
            else:
                match_value = int(match_string)
        except ValueError:
            return None
        match_context.update(match_string)
        return MatchElement("%s/%s" % (path, self.element_id), match_string, match_value, None)
