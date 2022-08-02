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
import re
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

    def __init__(self, element_id, **kwargs):
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
        @param delimiter a non-escaped delimiter string to search for.
        @param escape a character to escape in the string.
        @param consume_delimiter True if the delimiter character should also be consumed.
        @param value_model the ModelElement which has to match the data.
        @param value_path the relative path to the target value from the value_model element on. When the path does not resolve
               to a value, this model element will not match. A path value of None indicates, that the match element of the value_model
               should be used directly.
        @param branch_model_dict a dictionary to select a branch for the value identified by valuePath.
        @param default_branch when lookup in branch_model_dict fails, use this as default branch or fail when None.
        @param children a list of child elements to be iterated through.
        @param fixed_data a non-escaped delimiter string to search for.
        @param wordlist the list of words to search for. If it does not fulfill the sorting criteria mentioned in the class documentation,
               an Exception will be raised.
        @param ipv6 if True, IPv6 addresses are parsed, IPv4 addresses are parsed otherwise.
        @param key_parser_dict: A dictionary of all keys with the according parsers. If a key should be optional, the associated parser must
               start with the OptionalMatchModelElement. To allow every key in a JSON object use "key": "ALLOW_ALL". To allow only empty
               arrays - [] - use "key": "EMPTY_ARRAY". To allow only empty objects - {} - use "key": "EMPTY_OBJECT".
               To allow only empty strings - "" - use "key": "EMPTY_STRING". To allow all keys in an object for a parser use
               "ALLOW_ALL_KEYS": parser. To allow only null values use "key": "NULL_OBJECT".
        @param optional_key_prefix: If some key starts with the optional_key_prefix it will be considered optional.
        @param nullable_key_prefix: The value of this key may be null instead of any expected value.
        @param allow_all_fields: Unknown fields are skipped without parsing with any parsing model.
        @param optional_element the element to be optionally matched.
        @param repeated_element the MatchElement to be repeated in the data.
        @param min_repeat the minimum number of repeated matches of the repeated_element.
        @param max_repeat the maximum number of repeated matches of the repeated_element.
        @param upper_case if True, the letters of the hex alphabet are uppercase, otherwise they are lowercase.
        @param alphabet the allowed letters to match data.
        """

        allowed_kwargs = [
            "date_format", "time_zone", "text_locale", "start_year", "max_time_jump_seconds", "value_sign_type", "value_pad_type",
            "exponent_type", "delimiter", "escape", "consume_delimiter", "value_model", "value_path", "branch_model_dict", "default_branch",
            "children", "fixed_data", "wordlist", "ipv6", "key_parser_dict", "optional_key_prefix", "nullable_key_prefix",
            "allow_all_fields", "optional_element", "repeated_element", "min_repeat", "max_repeat", "upper_case", "alphabet"
        ]
        for argument, value in list(locals().items())[1:-1]:  # skip self parameter and kwargs
            if value is not None:
                setattr(self, argument, value)
        for argument, value in kwargs.items():  # skip self parameter and kwargs
            if argument not in allowed_kwargs:
                msg = f"Argument {argument} is unknown. Consider changing it or adding it to the allowed_kwargs list."
                logging.getLogger(DEBUG_LOG_NAME).error(msg)
                raise ValueError(msg)
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
            if not isinstance(self.date_format, bytes):
                msg = "date_format has to be of the type bytes."
                logging.getLogger(DEBUG_LOG_NAME).error(msg)
                raise TypeError(msg)
            if len(self.date_format) <= 1:
                msg = "At least one date_format specifier must be defined."
                logging.getLogger(DEBUG_LOG_NAME).error(msg)
                raise ValueError(msg)

        if hasattr(self, "text_locale"):
            if self.text_locale is not None:
                if not isinstance(self.text_locale, str) and not isinstance(self.text_locale, tuple):
                    msg = "text_locale has to be of the type string or of the type tuple and have the length 2. (locale, encoding)"
                    logging.getLogger(DEBUG_LOG_NAME).error(msg)
                    raise TypeError(msg)
                if isinstance(self.text_locale, tuple) and len(self.text_locale) != 2:
                    msg = "text_locale has to be of the type string or of the type tuple and have the length 2. (locale, encoding)"
                    logging.getLogger(DEBUG_LOG_NAME).error(msg)
                    raise ValueError(msg)
                try:
                    old_locale = locale.getdefaultlocale()
                    if old_locale != self.text_locale:
                        locale.setlocale(locale.LC_ALL, self.text_locale)
                        logging.getLogger(DEBUG_LOG_NAME).info(
                            "Changed time locale from %s to %s.", self.text_locale, "".join(self.text_locale))
                except locale.Error:
                    msg = "text_locale %s is not installed!" % self.text_locale
                    logging.getLogger(DEBUG_LOG_NAME).error(msg)
                    raise locale.Error(msg)

        if hasattr(self, "start_year"):
            if self.start_year is not None:
                if not isinstance(self.start_year, int) or isinstance(self.start_year, bool):
                    msg = "start_year has to be of the type integer."
                    logging.getLogger(DEBUG_LOG_NAME).error(msg)
                    raise TypeError(msg)

        if hasattr(self, "max_time_jump_seconds"):
            if not isinstance(self.max_time_jump_seconds, int) or isinstance(self.max_time_jump_seconds, bool):
                msg = "max_time_jump_seconds has to be of the type integer."
                logging.getLogger(DEBUG_LOG_NAME).error(msg)
                raise TypeError(msg)
            if self.max_time_jump_seconds <= 0:
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
            else:
                msg = "Invalid value_sign_type %s" % type(self.value_sign_type)
                logging.getLogger(DEBUG_LOG_NAME).error(msg)
                raise ValueError(msg)

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
            else:
                msg = "Invalid value_pad_type %s" % type(self.value_pad_type)
                logging.getLogger(DEBUG_LOG_NAME).error(msg)
                raise ValueError(msg)

        if hasattr(self, "exponent_type"):
            if not isinstance(self.exponent_type, str):
                msg = "exponent_type must be of type string. Current type: %s" % type(self.exponent_type)
                logging.getLogger(DEBUG_LOG_NAME).error(msg)
                raise TypeError(msg)
            if self.exponent_type not in [EXP_TYPE_NONE, EXP_TYPE_OPTIONAL, EXP_TYPE_MANDATORY]:
                msg = "Invalid exponent_type %s" % self.exponent_type
                logging.getLogger(DEBUG_LOG_NAME).error(msg)
                raise ValueError(msg)

        if hasattr(self, "delimiter"):
            if not isinstance(self.delimiter, bytes):
                msg = "delimiter has to be of the type bytes."
                logging.getLogger(DEBUG_LOG_NAME).error(msg)
                raise TypeError(msg)
            if len(self.delimiter) < 1:
                msg = "delimiter must not be empty."
                logging.getLogger(DEBUG_LOG_NAME).error(msg)
                raise ValueError(msg)

        if hasattr(self, "escape"):
            if self.escape is not None:
                if not isinstance(self.escape, bytes):
                    msg = "escape has to be of the type bytes."
                    logging.getLogger(DEBUG_LOG_NAME).error(msg)
                    raise TypeError(msg)
                if len(self.escape) < 1:
                    msg = "escape must not be empty."
                    logging.getLogger(DEBUG_LOG_NAME).error(msg)
                    raise ValueError(msg)
        if hasattr(self, "consume_delimiter"):
            if not isinstance(self.consume_delimiter, bool):
                msg = "consume_delimiter has to be of the type bool."
                logging.getLogger(DEBUG_LOG_NAME).error(msg)
                raise TypeError(msg)

        if hasattr(self, "value_model"):
            if not isinstance(self.value_model, ModelElementInterface):
                msg = "value_model has to be of the type ModelElementInterface."
                logging.getLogger(DEBUG_LOG_NAME).error(msg)
                raise TypeError(msg)

        if hasattr(self, "value_path"):
            if self.value_path is not None:
                if not isinstance(self.value_path, str):
                    msg = "value_path has to be of the type string or None."
                    logging.getLogger(DEBUG_LOG_NAME).error(msg)
                    raise TypeError(msg)
                if len(self.value_path) < 1:
                    msg = "value_path must not be empty."
                    logging.getLogger(DEBUG_LOG_NAME).error(msg)
                    raise ValueError(msg)

        if hasattr(self, "branch_model_dict"):
            if not isinstance(self.branch_model_dict, dict):
                msg = "branch_model_dict has to be of the type dict."
                logging.getLogger(DEBUG_LOG_NAME).error(msg)
                raise TypeError(msg)
            for val in self.branch_model_dict.values():
                if not isinstance(val, ModelElementInterface):
                    msg = "all branch_model_dict values have to be of the type ModelElementInterface."
                    logging.getLogger(DEBUG_LOG_NAME).error(msg)
                    raise TypeError(msg)

        if hasattr(self, "default_branch"):
            if self.default_branch is not None and not isinstance(self.default_branch, ModelElementInterface):
                msg = "default_branch has to be of the type string or None."
                logging.getLogger(DEBUG_LOG_NAME).error(msg)
                raise TypeError(msg)

        if hasattr(self, "children"):
            if not isinstance(self.children, list):
                msg = "children has to be of the type string."
                logging.getLogger(DEBUG_LOG_NAME).error(msg)
                raise TypeError(msg)
            if len(self.children) < 1:
                msg = "children must not be empty."
                logging.getLogger(DEBUG_LOG_NAME).error(msg)
                raise ValueError(msg)
            for child in self.children:
                if not isinstance(child, ModelElementInterface):
                    msg = "all children have to be of the type ModelElementInterface."
                    logging.getLogger(DEBUG_LOG_NAME).error(msg)
                    raise TypeError(msg)

        if hasattr(self, "fixed_data"):
            if not isinstance(self.fixed_data, bytes):
                msg = "fixed_data has to be of the type byte string."
                logging.getLogger(DEBUG_LOG_NAME).error(msg)
                raise TypeError(msg)
            if len(self.fixed_data) < 1:
                msg = "fixed_data must not be empty."
                logging.getLogger(DEBUG_LOG_NAME).error(msg)
                raise ValueError(msg)

        if hasattr(self, "wordlist"):
            if not isinstance(self.wordlist, list):
                msg = "wordlist has to be of the type list."
                logging.getLogger(DEBUG_LOG_NAME).error(msg)
                raise TypeError(msg)
            if len(self.wordlist) < 1:
                msg = "wordlist must have at least one element."
                logging.getLogger(DEBUG_LOG_NAME).error(msg)
                raise ValueError(msg)
            for word in self.wordlist:
                if not isinstance(word, bytes):
                    msg = "words from the wordlist must be of the type bytes."
                    logging.getLogger(DEBUG_LOG_NAME).error(msg)
                    raise TypeError(msg)

            for test_pos, ref_word in enumerate(self.wordlist):
                for test_word in self.wordlist[test_pos + 1:]:
                    if test_word.startswith(ref_word):
                        msg = "Word %s would be shadowed by word %s at lower position" % (repr(test_word), repr(ref_word))
                        logging.getLogger(DEBUG_LOG_NAME).error(msg)
                        raise ValueError(msg)

        if hasattr(self, "upper_case"):
            if not isinstance(self.upper_case, bool):
                msg = "upper_case has to be of the type bool."
                logging.getLogger(DEBUG_LOG_NAME).error(msg)
                raise TypeError(msg)
            if self.upper_case:
                self.hex_regex = re.compile(rb"[0-9A-F]+")
            else:
                self.hex_regex = re.compile(rb"[0-9a-f]+")

        if hasattr(self, "ipv6"):
            if not isinstance(self.ipv6, bool):
                msg = "ipv6 has to be of the type bool."
                logging.getLogger(DEBUG_LOG_NAME).error(msg)
                raise TypeError(msg)

        if hasattr(self, "key_parser_dict"):
            if not isinstance(self.key_parser_dict, dict):
                msg = "key_parser_dict has to be of the type dict."
                logging.getLogger(DEBUG_LOG_NAME).error(msg)
                raise TypeError(msg)

        if hasattr(self, "optional_key_prefix"):
            if not isinstance(self.optional_key_prefix, str):
                msg = "optional_key_prefix has to be of the type string."
                logging.getLogger(DEBUG_LOG_NAME).error(msg)
                raise TypeError(msg)
            if len(self.optional_key_prefix) < 1:
                msg = "optional_key_prefix must not be empty."
                logging.getLogger(DEBUG_LOG_NAME).error(msg)
                raise ValueError(msg)

        if hasattr(self, "nullable_key_prefix"):
            if not isinstance(self.nullable_key_prefix, str):
                msg = "nullable_key_prefix has to be of the type string."
                logging.getLogger(DEBUG_LOG_NAME).error(msg)
                raise TypeError(msg)
            if len(self.nullable_key_prefix) < 1:
                msg = "nullable_key_prefix must not be empty."
                logging.getLogger(DEBUG_LOG_NAME).error(msg)
                raise ValueError(msg)

        if hasattr(self, "optional_key_prefix") and hasattr(self, "nullable_key_prefix"):
            if self.optional_key_prefix == self.nullable_key_prefix:
                msg = "optional_key_prefix must not be the same as nullable_key_prefix!"
                logging.getLogger(DEBUG_LOG_NAME).error(msg)
                raise ValueError(msg)

        if hasattr(self, "allow_all_fields"):
            if not isinstance(self.allow_all_fields, bool):
                msg = "allow_all_fields has to be of the type bool."
                logging.getLogger(DEBUG_LOG_NAME).error(msg)
                raise TypeError(msg)

        if hasattr(self, "optional_element"):
            if not isinstance(self.optional_element, ModelElementInterface):
                msg = "optional_element has to be of the type ModelElementInterface."
                logging.getLogger(DEBUG_LOG_NAME).error(msg)
                raise TypeError(msg)

        if hasattr(self, "repeated_element"):
            if not isinstance(self.repeated_element, ModelElementInterface):
                msg = "repeated_element has to be of the type ModelElementInterface."
                logging.getLogger(DEBUG_LOG_NAME).error(msg)
                raise TypeError(msg)

        if hasattr(self, "min_repeat"):
            if not isinstance(self.min_repeat, int) or isinstance(self.min_repeat, bool):
                msg = "min_repeat has to be of the type integer."
                logging.getLogger(DEBUG_LOG_NAME).error(msg)
                raise TypeError(msg)
            if self.min_repeat < 0:
                msg = "min_repeat has to be >= 0."
                logging.getLogger(DEBUG_LOG_NAME).error(msg)
                raise ValueError(msg)

        if hasattr(self, "max_repeat"):
            if not isinstance(self.max_repeat, int) or isinstance(self.max_repeat, bool):
                msg = "max_repeat has to be of the type integer."
                logging.getLogger(DEBUG_LOG_NAME).error(msg)
                raise TypeError(msg)
            if self.max_repeat < 1 or self.min_repeat > self.max_repeat:
                msg = "max_repeat has to be >= 1 and max_repeat has to be bigger than min_repeat."
                logging.getLogger(DEBUG_LOG_NAME).error(msg)
                raise ValueError(msg)

        if hasattr(self, "alphabet"):
            if not isinstance(self.alphabet, bytes):
                msg = "alphabet has to be of the type bytes."
                logging.getLogger(DEBUG_LOG_NAME).error(msg)
                raise TypeError(msg)
            if len(self.alphabet) < 1:
                msg = "alphabet must not be empty."
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
