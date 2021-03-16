"""
This module contains a datetime parser and helper classes for parsing.

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


import datetime
import sys
import time
import logging
from dateutil.parser import parse

from aminer import AminerConfig
from aminer.parsing.ModelElementInterface import ModelElementInterface
from aminer.parsing.MatchElement import MatchElement


class DateTimeModelElement(ModelElementInterface):
    """
    This class defines a model element to parse date or datetime values.
    The element is similar to the strptime function but does not use it due to the numerous problems associated with it, e.g. no leap year
    support for semiqualified years, no %s (seconds since epoch) format in Python strptime, no %f support in libc strptime, no support to
    determine the length of the parsed string.
    """

    # skipcq: PYL-W0613
    def __init__(self, path_id, date_format, time_zone=None, text_locale=None, start_year=None, max_time_jump_seconds=86400):
        """
        Create a DateTimeModelElement to parse dates using a custom, timezone and locale-aware implementation similar to strptime.
        @param date_format, is a byte string that represents the date format for parsing, see Python strptime specification for
        available formats. Supported format specifiers are:
            * %b: month name in current locale
            * %d: day in month, can be space or zero padded when followed by separator or at end of string.
            * %f: fraction of seconds (the digits after the the '.')
            * %H: hours from 00 to 23
            * %M: minutes
            * %m: two digit month number
            * %S: seconds
            * %s: seconds since the epoch (1970-01-01)
            * %Y: 4 digit year number
            * %z: detect and parse timezone strings like UTC, CET, +0001, etc. automatically.
        Common formats are:
            * '%b %d %H:%M:%S' e.g. for 'Nov 19 05:08:43'
        @param time_zone the timezone for parsing the values or UTC when None.
        @param text_locale the locale to use for parsing the day, month names or None to use the default locale. Locale changing is
        not yet implemented, use locale.setlocale() in global configuration.
        @param start_year when parsing date records without any year information, assume this is the year of the first value parsed.
        @param max_time_jump_seconds for detection of year wraps with date formats missing year information, also the current time
        of values has to be tracked. This value defines the window within that the time may jump between two matches. When not
        within that window, the value is still parsed, corrected to the most likely value but does not change the detection year.
        """
        self.path_id = path_id
        self.time_zone = time_zone
        if time_zone is None:
            self.time_zone = datetime.datetime.now(datetime.timezone.utc).astimezone().tzinfo
        # Make sure that dateFormat is valid and extract the relevant parts from it.
        self.format_has_year_flag = False
        self.format_has_tz_specifier = False
        self.tz_specifier_offset = None
        self.tz_specifier_offset_str = None
        self.tz_specifier_format_length = -1
        self.date_format_parts = None
        self.scan_date_format(date_format)

        self.start_year = start_year
        if (not self.format_has_year_flag) and (start_year is None):
            self.start_year = time.gmtime(None).tm_year
        self.max_time_jump_seconds = max_time_jump_seconds
        self.last_parsed_seconds = 0
        self.epoch_start_time = datetime.datetime.fromtimestamp(0, self.time_zone)

    def scan_date_format(self, date_format):
        """Scan the date format."""
        if self.date_format_parts is not None:
            msg = 'Cannot rescan date format after initialization'
            logging.getLogger(AminerConfig.DEBUG_LOG_NAME).error(msg)
            raise Exception(msg)
        date_format_parts = []
        date_format_type_set = set()
        scan_pos = 0
        while scan_pos < len(date_format):
            next_param_pos = date_format.find(b'%', scan_pos)
            if next_param_pos < 0:
                next_param_pos = len(date_format)
            new_element = None
            if next_param_pos != scan_pos:
                new_element = date_format[scan_pos:next_param_pos]
            else:
                param_type_code = date_format[next_param_pos + 1:next_param_pos + 2]
                next_param_pos = scan_pos + 2
                if param_type_code == b'%':
                    new_element = b'%'
                elif param_type_code == b'b':
                    import calendar
                    name_dict = {}
                    for month_pos in range(1, 13):
                        name_dict[calendar.month_name[month_pos][:3].encode()] = month_pos
                    new_element = (1, 3, name_dict)
                elif param_type_code == b'd':
                    new_element = (2, 2, int)
                elif param_type_code == b'f':
                    new_element = (6, -1, DateTimeModelElement.parse_fraction)
                elif param_type_code == b'H':
                    new_element = (3, 2, int)
                elif param_type_code == b'M':
                    new_element = (4, 2, int)
                elif param_type_code == b'm':
                    new_element = (1, 2, int)
                elif param_type_code == b'S':
                    new_element = (5, 2, int)
                elif param_type_code == b's':
                    new_element = (7, -1, int)
                elif param_type_code == b'Y':
                    self.format_has_year_flag = True
                    new_element = (0, 4, int)
                elif param_type_code == b'z':
                    self.format_has_tz_specifier = True
                    scan_pos = next_param_pos
                    continue
                else:
                    msg = 'Unknown dateformat specifier %s' % repr(param_type_code)
                    logging.getLogger(AminerConfig.DEBUG_LOG_NAME).error(msg)
                    raise Exception(msg)
            if isinstance(new_element, bytes):
                if date_format_parts and (isinstance(date_format_parts[-1], bytes)):
                    date_format_parts[-1] += new_element
                else:
                    date_format_parts.append(new_element)
            else:
                if new_element[0] in date_format_type_set:
                    msg = 'Multiple format specifiers for type %d' % new_element[0]
                    logging.getLogger(AminerConfig.DEBUG_LOG_NAME).error(msg)
                    raise Exception(msg)
                date_format_type_set.add(new_element[0])
                date_format_parts.append(new_element)
            scan_pos = next_param_pos
        if (7 in date_format_type_set) and (not date_format_type_set.isdisjoint(set(range(0, 6)))):
            msg = 'Cannot use %%s (seconds since epoch) with other non-second format types'
            logging.getLogger(AminerConfig.DEBUG_LOG_NAME).error(msg)
            raise Exception(msg)
        self.date_format_parts = date_format_parts

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
        Try to find a match on given data for this model element and all its children.
        When a match is found, the matchContext is updated accordingly.
        @return None when there is no match, MatchElement otherwise. The matchObject returned is a tuple containing the datetime
        object and the seconds since 1970
        """
        parse_pos = 0
        # Year, month, day, hour, minute, second, fraction, gmt-seconds:
        result = [None, None, None, None, None, None, None, None]
        for part_pos, date_format_part in enumerate(self.date_format_parts):
            if isinstance(date_format_part, bytes):
                if not match_context.match_data[parse_pos:].startswith(date_format_part):
                    return None
                parse_pos += len(date_format_part)
                continue
            next_length = date_format_part[1]
            next_data = None
            if next_length < 0:
                # No length given: this is only valid for integer fields or fields followed by a separator string.
                if (part_pos + 1) < len(self.date_format_parts):
                    next_part = self.date_format_parts[part_pos + 1]
                    if isinstance(next_part, bytes):
                        end_pos = match_context.match_data.find(next_part, parse_pos)
                        if end_pos < 0:
                            return None
                        next_length = end_pos - parse_pos
                if next_length < 0:
                    # No separator, so get the number of decimal digits.
                    next_length = 0
                    for digit_ord in match_context.match_data[parse_pos:]:
                        if (digit_ord < 0x30) or (digit_ord > 0x39):
                            break
                        next_length += 1
                    if next_length == 0:
                        return None
                next_data = match_context.match_data[parse_pos:parse_pos + next_length]
            else:
                next_data = match_context.match_data[parse_pos:parse_pos + next_length]
                if len(next_data) != next_length:
                    return None
            parse_pos += next_length
            transform_function = date_format_part[2]
            if isinstance(transform_function, dict):
                value = None
                try:
                    value = transform_function.get(next_data, None)
                except ValueError:
                    pass
                if value is None:
                    return None
                result[date_format_part[0]] = value
            else:
                try:
                    result[date_format_part[0]] = transform_function(next_data)
                # skipcq: FLK-E722
                except:
                    # Parsing failed, most likely due to wrong format.
                    return None

        date_str = match_context.match_data[:parse_pos]

        # Now combine the values and build the final value.
        parsed_date_time = None
        total_seconds = result[7]
        if total_seconds is not None:  # skipcq: PTC-W0048
            if result[6] is not None:
                total_seconds += result[6]
        # For epoch second formats, the datetime value usually is not important. So stay with parsed_date_time to none.
        else:
            if not self.format_has_year_flag:
                result[0] = self.start_year
            microseconds = 0
            if result[6] is not None:
                microseconds = int(result[6] * 1000000)
            try:
                for i, x in enumerate(result):
                    if x is None:
                        result[i] = 0
                parsed_date_time = datetime.datetime(result[0], result[1], result[2], result[3], result[4], result[5], microseconds,
                                                     self.time_zone)
            # skipcq: FLK-E722
            except:
                # The values did not form a valid datetime object, e.g. when the day of month is out of range. The rare case where dates
                # without year are parsed and the last parsed timestamp was from the previous non-leap year but the current timestamp is it,
                # is ignored. Values that sparse and without a year number are very likely to result in invalid data anyway.
                return None

            # Avoid timedelta.total_seconds(), not supported in Python 2.6.
            delta = parsed_date_time - self.epoch_start_time
            total_seconds = (delta.days * 86400 + delta.seconds)

            # See if this is change from one year to next.
            if not self.format_has_year_flag:
                if self.last_parsed_seconds == 0:
                    # There cannot be a wraparound if we do not know any previous time values yet.
                    self.last_parsed_seconds = total_seconds
                else:
                    delta = self.last_parsed_seconds - total_seconds
                    if abs(delta) <= self.max_time_jump_seconds:
                        self.last_parsed_seconds = total_seconds
                    else:
                        # This might be the first date value for the next year or one from the previous.
                        # Test both cases and see, what is more likely.
                        next_year_date_time = parsed_date_time.replace(self.start_year + 1)
                        delta = next_year_date_time - self.epoch_start_time
                        next_year_total_seconds = (delta.days * 86400 + delta.seconds)
                        if next_year_total_seconds - self.last_parsed_seconds <= self.max_time_jump_seconds:
                            self.start_year += 1
                            parsed_date_time = next_year_date_time
                            total_seconds = next_year_total_seconds
                            self.last_parsed_seconds = total_seconds
                            msg = 'DateTimeModelElement unqualified timestamp year wraparound detected from %s to %s' % (
                                datetime.datetime.fromtimestamp(self.last_parsed_seconds, self.time_zone).isoformat(),
                                parsed_date_time.isoformat())
                            logging.getLogger(AminerConfig.DEBUG_LOG_NAME).warning(msg)
                            print('WARNING: ' + msg, file=sys.stderr)
                        else:
                            last_year_date_time = parsed_date_time.replace(self.start_year - 1)
                            delta = last_year_date_time - self.epoch_start_time
                            last_year_total_seconds = (delta.days * 86400 + delta.seconds)
                            if self.last_parsed_seconds - last_year_total_seconds <= self.max_time_jump_seconds:
                                parsed_date_time = last_year_date_time
                                total_seconds = last_year_total_seconds
                                self.last_parsed_seconds = total_seconds
                            else:
                                # None of both seems correct, just report that.
                                msg = 'DateTimeModelElement time inconsistencies parsing %s, expecting value around %d. ' \
                                      'Check your settings!' % (repr(date_str), self.last_parsed_seconds)
                                logging.getLogger(AminerConfig.DEBUG_LOG_NAME).warning(msg)
                                print('WARNING: ' + msg, file=sys.stderr)

            # We discarded the parsed_date_time microseconds beforehand, use the full float value here instead of the rounded integer.
            if result[6] is not None:
                total_seconds += result[6]

        if self.format_has_tz_specifier and self.tz_specifier_format_length == -1:
            start = 0
            while start < parse_pos:
                try:
                    parse(match_context.match_data[start:parse_pos])
                    break
                # skipcq: FLK-E722
                except:
                    start += 1
            self.tz_specifier_format_length = len(match_context.match_data)
            # try to find the longest matching date
            while True:
                try:
                    parse(match_context.match_data[start:self.tz_specifier_format_length])
                    break
                # skipcq: FLK-E722
                except:
                    self.tz_specifier_format_length -= 1
                    if self.tz_specifier_format_length <= 0:
                        msg = "The date_format could not be found."
                        logging.getLogger(AminerConfig.DEBUG_LOG_NAME).error(msg)
                        raise Exception(msg)

        match_context.update(date_str)
        if self.format_has_tz_specifier:
            if self.tz_specifier_format_length < parse_pos and (b'+' in match_context.match_data or b'-' in match_context.match_data):
                data = match_context.match_data.split(b'+')
                if len(data) == 1:
                    data = match_context.match_data.split(b'-')
                for i in range(1, 5):
                    if not match_context.match_data[i:i+1].decode('utf-8').isdigit():
                        i -= 1
                        break
                self.tz_specifier_format_length = len(data[0]) + i + 1
                parse_pos = 0

            remaining_data = match_context.match_data[:self.tz_specifier_format_length-parse_pos]
            match_context.update(remaining_data)
            if self.tz_specifier_offset is None:
                # initialize tz_specifier variables. The first values are expected to match the time_zone argument.
                self.tz_specifier_offset = 0
                self.tz_specifier_offset_str = remaining_data
            # check if the remaining_data has changed
            elif remaining_data != self.tz_specifier_offset_str:
                sign = 1
                data = remaining_data.split(b'+')
                if len(data) == 1:
                    data = remaining_data.split(b'-')
                    sign = -1
                    if len(data) == 1:
                        data = None
                # only add offset if a + or - sign is used.
                if data is not None:
                    old_data = self.tz_specifier_offset_str.split(b'+')
                    if len(old_data) == 1:
                        old_data = remaining_data.split(b'-')
                    self.tz_specifier_offset = (int(data[1]) - int(old_data[1]))*sign
                    self.tz_specifier_offset_str = remaining_data
                # if no + or - sign is found no offset is added.
                else:
                    self.tz_specifier_offset = 0
                    self.tz_specifier_offset_str = remaining_data
            return MatchElement("%s/%s" % (path, self.path_id), date_str+remaining_data, total_seconds+self.tz_specifier_offset*3600, None)
        return MatchElement("%s/%s" % (path, self.path_id), date_str, total_seconds, None)

    @staticmethod
    def parse_fraction(value_str):
        """Pass this method as function pointer to the parsing logic."""
        return float(b'0.' + value_str)
