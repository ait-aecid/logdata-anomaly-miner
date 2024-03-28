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
        """
        Initialize the ModelElement.
        @param element_id an identifier for the ModelElement which is shown in the path.
        @param value_sign_type defines the possible start characters in the value. With the SIGN_TYPE_NONE only digits are allowed,
               with SIGN_TYPE_OPTIONAL digits and a minus sign are allowed and with SIGN_TYPE_MANDATORY the value must start with + or -.
        @param value_pad_type defines the padding values which can prefix the numerical value. With PAD_TYPE_NONE no padding is allowed,
               PAD_TYPE_ZERO allows zeros before the value and PAD_TYPE_BLANK allows spaces before the value.
        @param exponent_type defines the allowed types of exponential values. With EXP_TYPE_NONE no exponential values are allowed,
               EXP_TYPE_OPTIONAL allows exponential values and with EXP_TYPE_MANDATORY every value must contain exponential values.
        """
        super().__init__(element_id, value_sign_type=value_sign_type, value_pad_type=value_pad_type, exponent_type=exponent_type)
        self.digits = set(b"0123456789")

    def get_match_element(self, path: str, match_context):
        """
        Find the maximum number of bytes forming a decimal number according to the parameters specified.
        @param path to be printed in the MatchElement.
        @param match_context the match_context to be analyzed.
        @return a match when at least one byte being a digit was found
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

        if match_len == 1:
            if data[0] not in self.digits:
                return None
        elif num_start_pos == match_len and match_len == 1:  # only return None if match_len is 1 to allow 00 with zero padding.
            return None

        # See if there is decimal part after decimal point.
        if (match_len < len(data)) and (chr(data[match_len]) == "."):
            match_len += 1
            post_point_start = match_len
            for test_byte in data[match_len:]:
                if test_byte not in self.digits:
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
                if test_byte not in self.digits:
                    break
                match_len += 1
            if match_len == exp_number_start:
                # No exponent number found.
                return None
        elif self.exponent_type == DecimalFloatValueModelElement.EXP_TYPE_MANDATORY:
            return None

        match_string = data[:match_len]
        if self.pad_characters == b" " and match_string[0] in b"+-":
            if b" " in match_string.replace(b" ", b"", 1):
                return None
            match_value = float(match_string.replace(b" ", b"", 1))
        else:
            match_value = float(match_string)
        match_context.update(match_string)
        return MatchElement(f"{path}/{self.element_id}", match_string, match_value, None)
