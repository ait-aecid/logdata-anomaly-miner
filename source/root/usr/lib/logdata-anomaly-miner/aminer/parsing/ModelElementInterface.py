"""This module defines various interfaces for log atom parsing and namespace shortcuts to the ModelElements.

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

import abc
import locale
import logging
from aminer.AminerConfig import DEBUG_LOG_NAME

SIGN_TYPE_NONE = "none"
SIGN_TYPE_OPTIONAL = "optional"
SIGN_TYPE_MANDATORY = "mandatory"

PAD_TYPE_NONE = "none"
PAD_TYPE_ZERO = "zero"
PAD_TYPE_BLANK = "blank"

EXP_TYPE_NONE = "none"
EXP_TYPE_OPTIONAL = "optional"
EXP_TYPE_MANDATORY = "mandatory"


class ModelElementInterface(metaclass=abc.ABCMeta):
    """This is the superinterface of all model elements."""

    def __init__(
            self, element_id, date_format=None, time_zone=None, text_locale=None, start_year=None, max_time_jump_seconds=None,
            value_sign_type=None, value_pad_type=None, exponent_type=None
    ):
        """
        Initialize the ModelElement.
        @param element_id an identifier for the ModelElement which is shown in the path.
        @param date_format, is a byte string that represents the date format for parsing, see Python strptime specification for
               available formats. Supported format specifiers are:
                 * %b: month name in current locale
                 * %d: day in month, can be space or zero padded when followed by separator or at end of string.
                 * %f: fraction of seconds (the digits after the the ".")
                 * %H: hours from 00 to 23
                 * %M: minutes
                 * %m: two digit month number
                 * %S: seconds
                 * %s: seconds since the epoch (1970-01-01)
                 * %Y: 4 digit year number
                 * %z: detect and parse timezone strings like UTC, CET, +0001, etc. automatically.
               Common formats are:
                 * "%b %d %H:%M:%S" e.g. for "Nov 19 05:08:43"
                 * "%d.%m.%YT%H:%M:%S" e.g. for "07.02.2019T11:40:00"
                 * "%d.%m.%Y %H:%M:%S.%f" e.g. for "07.02.2019 11:40:00.123456"
                 * "%d.%m.%Y %H:%M:%S%z" e.g. for "07.02.2019 11:40:00+0000" or "07.02.2019 11:40:00 UTC"
                 * "%d.%m.%Y" e.g. for "07.02.2019"
                 * "%H:%M:%S" e.g. for "11:40:23"
        @param time_zone the timezone for parsing the values or UTC when None.
        @param text_locale the locale to use for parsing the day, month names or None to use the default locale. The locale must be a tuple
               of (locale, encoding) or a string.
        @param start_year when parsing date records without any year information, assume this is the year of the first value parsed.
        @param max_time_jump_seconds for detection of year wraps with date formats missing year information, also the current time
               of values has to be tracked. This value defines the window within that the time may jump between two matches. When not
               within that window, the value is still parsed, corrected to the most likely value but does not change the detection year.
        @param value_sign_type defines the possible start characters in the value. With the SIGN_TYPE_NONE only digits are allowed,
               with SIGN_TYPE_OPTIONAL digits and a minus sign are allowed and with SIGN_TYPE_MANDATORY the value must start with + or -.
        @param value_pad_type defines the padding values which can prefix the numerical value. With PAD_TYPE_NONE no padding is allowed,
               PAD_TYPE_ZERO allows zeros before the value and PAD_TYPE_BLANK allows spaces before the value.
        @param exponent_type defines the allowed types of exponential values. With EXP_TYPE_NONE no exponential values are allowed,
               EXP_TYPE_OPTIONAL allows exponential values and with EXP_TYPE_MANDATORY every value must contain exponential values.
        """
        for argument, value in list(locals().items())[1:]:  # skip self parameter
            if value is not None:
                setattr(self, argument, value)

        if not isinstance(element_id, str):
            msg = "element_id has to be of the type string."
            logging.getLogger(DEBUG_LOG_NAME).error(msg)
            raise TypeError(msg)
        if len(element_id) < 1:
            msg = "element_id must not be empty."
            logging.getLogger(DEBUG_LOG_NAME).error(msg)
            raise ValueError(msg)

        if hasattr(self, "date_format"):
            if not isinstance(date_format, bytes):
                msg = "date_format has to be of the type bytes."
                logging.getLogger(DEBUG_LOG_NAME).error(msg)
                raise TypeError(msg)
            if len(date_format) <= 1:
                msg = "At least one date_format specifier must be defined."
                logging.getLogger(DEBUG_LOG_NAME).error(msg)
                raise ValueError(msg)

        if hasattr(self, "text_locale") and self.text_locale is not None:
            if not isinstance(text_locale, str) and not isinstance(text_locale, tuple):
                msg = "text_locale has to be of the type string or of the type tuple and have the length 2. (locale, encoding)"
                logging.getLogger(DEBUG_LOG_NAME).error(msg)
                raise TypeError(msg)
            if isinstance(text_locale, tuple) and len(text_locale) != 2:
                msg = "text_locale has to be of the type string or of the type tuple and have the length 2. (locale, encoding)"
                logging.getLogger(DEBUG_LOG_NAME).error(msg)
                raise ValueError(msg)
            try:
                old_locale = locale.getdefaultlocale()
                if old_locale != text_locale:
                    locale.setlocale(locale.LC_ALL, text_locale)
                    logging.getLogger(DEBUG_LOG_NAME).info("Changed time locale from %s to %s.", text_locale, "".join(text_locale))
            except locale.Error:
                msg = "text_locale %s is not installed!" % text_locale
                logging.getLogger(DEBUG_LOG_NAME).error(msg)
                raise locale.Error(msg)

        if hasattr(self, "start_year") and not isinstance(self.start_year, int) or isinstance(start_year, bool):
            msg = "start_year has to be of the type integer."
            logging.getLogger(DEBUG_LOG_NAME).error(msg)
            raise TypeError(msg)

        if hasattr(self, "max_time_jump_seconds"):
            if not isinstance(self.max_time_jump_seconds, int) or isinstance(self.max_time_jump_seconds, bool):
                msg = "max_time_jump_seconds has to be of the type integer."
                logging.getLogger(DEBUG_LOG_NAME).error(msg)
                raise TypeError(msg)
            if max_time_jump_seconds <= 0:
                msg = "max_time_jump_seconds must not be lower than 1 second."
                logging.getLogger(DEBUG_LOG_NAME).error(msg)
                raise ValueError(msg)

        if hasattr(self, "value_sign_type"):
            if not isinstance(self.value_sign_type, str):
                msg = "value_sign_type must be of type string. Current type: %s" % self.value_sign_type
                logging.getLogger(DEBUG_LOG_NAME).error(msg)
                raise TypeError(msg)
            if self.value_sign_type == SIGN_TYPE_NONE:
                self.start_characters = set(b"0123456789")
            elif self.value_sign_type == SIGN_TYPE_OPTIONAL:
                self.start_characters = set(b"-0123456789")
            elif self.value_sign_type == SIGN_TYPE_MANDATORY:
                self.start_characters = set(b"+-")

        if hasattr(self, "value_pad_type"):
            self.pad_characters = b""
            if not isinstance(self.value_pad_type, str):
                msg = "value_pad_type must be of type string. Current type: %s" % self.value_pad_type
                logging.getLogger(DEBUG_LOG_NAME).error(msg)
                raise TypeError(msg)
            if self.value_pad_type == PAD_TYPE_NONE:
                pass
            elif self.value_pad_type == PAD_TYPE_ZERO:
                self.pad_characters = b"0"
            elif self.value_pad_type == PAD_TYPE_BLANK:
                self.pad_characters = b" "

        if hasattr(self, "exponent_type"):
            if self.exponent_type not in [EXP_TYPE_NONE, EXP_TYPE_OPTIONAL, EXP_TYPE_MANDATORY]:
                msg = "Invalid exponent_type %s" % self.exponent_type
                logging.getLogger(DEBUG_LOG_NAME).error(msg)
                raise ValueError(msg)

    @abc.abstractmethod
    def get_match_element(self, path, match_context):
        """
        Try to find a match on given data for this model element and all its children.
        When a match is found, the matchContext is updated accordingly.
        @param path the model path to the parent model element invoking this method.
        @param match_context an instance of MatchContext class holding the data context to match against.
        @return the match_element or None if model did not match.
        """
