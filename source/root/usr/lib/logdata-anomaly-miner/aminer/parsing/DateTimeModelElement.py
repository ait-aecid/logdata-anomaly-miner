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


import sys
import time
import logging
import locale
from dateutil.parser import parse
from datetime import timezone, datetime

from aminer import AminerConfig
from aminer.parsing.ModelElementInterface import ModelElementInterface
from aminer.parsing.MatchElement import MatchElement

timezone_info = {
    "A": 1 * 3600, "ACDT": 10.5 * 3600, "ACST": 9.5 * 3600, "ACT": -5 * 3600, "ACWST": 8.75 * 3600, "ADT": 4 * 3600,
    "AEDT": 11 * 3600, "AEST": 10 * 3600, "AET": 10 * 3600, "AFT": 4.5 * 3600, "AKDT": -8 * 3600, "AKST": -9 * 3600, "ALMT": 6 * 3600,
    "AMST": -3 * 3600, "AMT": -4 * 3600, "ANAST": 12 * 3600, "ANAT": 12 * 3600, "AQTT": 5 * 3600, "ART": -3 * 3600, "AST": 3 * 3600,
    "AT": -4 * 3600, "AWDT": 9 * 3600, "AWST": 8 * 3600, "AZOST": 0 * 3600, "AZOT": -1 * 3600, "AZST": 5 * 3600, "AZT": 4 * 3600,
    "AoE": -12 * 3600, "B": 2 * 3600, "BNT": 8 * 3600, "BOT": -4 * 3600, "BRST": -2 * 3600, "BRT": -3 * 3600, "BST": 6 * 3600,
    "BTT": 6 * 3600, "C": 3 * 3600, "CAST": 8 * 3600, "CAT": 2 * 3600, "CCT": 6.5 * 3600, "CDT": -5 * 3600, "CEST": 2 * 3600,
    "CET": 1 * 3600, "CHADT": 13.75 * 3600, "CHAST": 12.75 * 3600, "CHOST": 9 * 3600, "CHOT": 8 * 3600, "CHUT": 10 * 3600,
    "CIDST": -4 * 3600, "CIST": -5 * 3600, "CKT": -10 * 3600, "CLST": -3 * 3600, "CLT": -4 * 3600, "COT": -5 * 3600, "CST": -6 * 3600,
    "CT": -6 * 3600, "CVT": -1 * 3600, "CXT": 7 * 3600, "ChST": 10 * 3600, "D": 4 * 3600, "DAVT": 7 * 3600, "DDUT": 10 * 3600,
    "E": 5 * 3600, "EASST": -5 * 3600, "EAST": -6 * 3600, "EAT": 3 * 3600, "ECT": -5 * 3600, "EDT": -4 * 3600, "EEST": 3 * 3600,
    "EET": 2 * 3600, "EGST": 0 * 3600, "EGT": -1 * 3600, "EST": -5 * 3600, "ET": -5 * 3600, "F": 6 * 3600, "FET": 3 * 3600,
    "FJST": 13 * 3600, "FJT": 12 * 3600, "FKST": -3 * 3600, "FKT": -4 * 3600, "FNT": -2 * 3600, "G": 7 * 3600, "GALT": -6 * 3600,
    "GAMT": -9 * 3600, "GET": 4 * 3600, "GFT": -3 * 3600, "GILT": 12 * 3600, "GMT": 0 * 3600, "GST": 4 * 3600, "GYT": -4 * 3600,
    "H": 8 * 3600, "HDT": -9 * 3600, "HKT": 8 * 3600, "HOVST": 8 * 3600, "HOVT": 7 * 3600, "HST": -10 * 3600, "I": 9 * 3600,
    "ICT": 7 * 3600, "IDT": 3 * 3600, "IOT": 6 * 3600, "IRDT": 4.5 * 3600, "IRKST": 9 * 3600, "IRKT": 8 * 3600, "IRST": 3.5 * 3600,
    "IST": 5.5 * 3600, "JST": 9 * 3600, "K": 10 * 3600, "KGT": 6 * 3600, "KOST": 11 * 3600, "KRAST": 8 * 3600, "KRAT": 7 * 3600,
    "KST": 9 * 3600, "KUYT": 4 * 3600, "L": 11 * 3600, "LHDT": 11 * 3600, "LHST": 10.5 * 3600, "LINT": 14 * 3600, "M": 12 * 3600,
    "MAGST": 12 * 3600, "MAGT": 11 * 3600, "MART": 9.5 * 3600, "MAWT": 5 * 3600, "MDT": -6 * 3600, "MHT": 12 * 3600, "MMT": 6.5 * 3600,
    "MSD": 4 * 3600, "MSK": 3 * 3600, "MST": -7 * 3600, "MT": -7 * 3600, "MUT": 4 * 3600, "MVT": 5 * 3600, "MYT": 8 * 3600, "N": -1 * 3600,
    "NCT": 11 * 3600, "NDT": 2.5 * 3600, "NFT": 11 * 3600, "NOVST": 7 * 3600, "NOVT": 7 * 3600, "NPT": 5.5 * 3600, "NRT": 12 * 3600,
    "NST": 3.5 * 3600, "NUT": -11 * 3600, "NZDT": 13 * 3600, "NZST": 12 * 3600, "O": -2 * 3600, "OMSST": 7 * 3600, "OMST": 6 * 3600,
    "ORAT": 5 * 3600, "P": -3 * 3600, "PDT": -7 * 3600, "PET": -5 * 3600, "PETST": 12 * 3600, "PETT": 12 * 3600, "PGT": 10 * 3600,
    "PHOT": 13 * 3600, "PHT": 8 * 3600, "PKT": 5 * 3600, "PMDT": -2 * 3600, "PMST": -3 * 3600, "PONT": 11 * 3600, "PST": -8 * 3600,
    "PT": -8 * 3600, "PWT": 9 * 3600, "PYST": -3 * 3600, "PYT": -4 * 3600, "Q": -4 * 3600, "QYZT": 6 * 3600, "R": -5 * 3600,
    "RET": 4 * 3600, "ROTT": -3 * 3600, "S": -6 * 3600, "SAKT": 11 * 3600, "SAMT": 4 * 3600, "SAST": 2 * 3600, "SBT": 11 * 3600,
    "SCT": 4 * 3600, "SGT": 8 * 3600, "SRET": 11 * 3600, "SRT": -3 * 3600, "SST": -11 * 3600, "SYOT": 3 * 3600, "T": -7 * 3600,
    "TAHT": -10 * 3600, "TFT": 5 * 3600, "TJT": 5 * 3600, "TKT": 13 * 3600, "TLT": 9 * 3600, "TMT": 5 * 3600, "TOST": 14 * 3600,
    "TOT": 13 * 3600, "TRT": 3 * 3600, "TVT": 12 * 3600, "U": -8 * 3600, "ULAST": 9 * 3600, "ULAT": 8 * 3600, "UTC": 0 * 3600,
    "UYST": -2 * 3600, "UYT": -3 * 3600, "UZT": 5 * 3600, "V": -9 * 3600, "VET": -4 * 3600, "VLAST": 11 * 3600, "VLAT": 10 * 3600,
    "VOST": 6 * 3600, "VUT": 11 * 3600, "W": -10 * 3600, "WAKT": 12 * 3600, "WARST": -3 * 3600, "WAST": 2 * 3600, "WAT": 1 * 3600,
    "WEST": 1 * 3600, "WET": 0 * 3600, "WFT": 12 * 3600, "WGST": -2 * 3600, "WGT": -3 * 3600, "WIB": 7 * 3600, "WIT": 9 * 3600,
    "WITA": 8 * 3600, "WST": 14 * 3600, "WT": 0 * 3600, "X": -11 * 3600, "Y": -12 * 3600, "YAKST": 10 * 3600, "YAKT": 9 * 3600,
    "YAPT": 10 * 3600, "YEKST": 6 * 3600, "YEKT": 5 * 3600, "Z": 0 * 3600}


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
        @param text_locale the locale to use for parsing the day, month names or None to use the default locale. The locale must be a tuple
        of (locale, encoding).
        @param start_year when parsing date records without any year information, assume this is the year of the first value parsed.
        @param max_time_jump_seconds for detection of year wraps with date formats missing year information, also the current time
        of values has to be tracked. This value defines the window within that the time may jump between two matches. When not
        within that window, the value is still parsed, corrected to the most likely value but does not change the detection year.
        """
        if not isinstance(path_id, str):
            msg = "path_id has to be of the type string."
            logging.getLogger(AminerConfig.DEBUG_LOG_NAME).error(msg)
            raise TypeError(msg)
        if len(path_id) < 1:
            msg = "path_id must not be empty."
            logging.getLogger(AminerConfig.DEBUG_LOG_NAME).error(msg)
            raise ValueError(msg)
        self.path_id = path_id
        self.time_zone = time_zone
        if time_zone is None:
            self.time_zone = timezone.utc
        self.text_locale = text_locale
        if text_locale is not None:
            if not isinstance(text_locale, str) and (not isinstance(text_locale, tuple) or isinstance(
                    text_locale, tuple) and len(text_locale) != 2):
                msg = "text_locale has to be of the type string or of the type tuple and have the length 2. (locale, encoding)"
                logging.getLogger(AminerConfig.DEBUG_LOG_NAME).error(msg)
                raise TypeError(msg)
            try:
                old_locale = locale.getdefaultlocale()
                if old_locale != text_locale:
                    locale.setlocale(locale.LC_ALL, text_locale)
                    logging.getLogger(AminerConfig.DEBUG_LOG_NAME).info("Changed time locale from %s to %s.", text_locale,
                                                                        "".join(text_locale))
            except locale.Error:
                msg = "text_locale %s is not installed!" % text_locale
                logging.getLogger(AminerConfig.DEBUG_LOG_NAME).error(msg)
                raise locale.Error(msg)
        # Make sure that dateFormat is valid and extract the relevant parts from it.
        self.format_has_year_flag = False
        self.format_has_tz_specifier = False
        self.tz_specifier_offset = None
        self.tz_specifier_offset_str = None
        self.tz_specifier_format_length = -1
        self.date_format_parts = None
        self.date_format = date_format
        if len(date_format) <= 1:
            msg = "At least one date_format specifier must be defined."
            logging.getLogger(AminerConfig.DEBUG_LOG_NAME).error(msg)
            raise ValueError(msg)
        self.scan_date_format(date_format)

        if start_year is not None and not isinstance(start_year, int) or isinstance(start_year, bool):
            msg = "start_year has to be of the type integer."
            logging.getLogger(AminerConfig.DEBUG_LOG_NAME).error(msg)
            raise TypeError(msg)
        self.start_year = start_year
        if (not self.format_has_year_flag) and (start_year is None):
            self.start_year = time.gmtime(None).tm_year

        if max_time_jump_seconds is not None and not isinstance(max_time_jump_seconds, int) or isinstance(max_time_jump_seconds, bool):
            msg = "max_time_jump_seconds has to be of the type integer."
            logging.getLogger(AminerConfig.DEBUG_LOG_NAME).error(msg)
            raise TypeError(msg)
        if max_time_jump_seconds <= 0:
            msg = "max_time_jump_seconds must not be lower than 1 second."
            logging.getLogger(AminerConfig.DEBUG_LOG_NAME).error(msg)
            raise ValueError(msg)
        self.max_time_jump_seconds = max_time_jump_seconds
        self.last_parsed_seconds = 0
        self.epoch_start_time = datetime.fromtimestamp(0, self.time_zone)

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
                    raise ValueError(msg)
            if isinstance(new_element, bytes):
                if date_format_parts and (isinstance(date_format_parts[-1], bytes)):
                    date_format_parts[-1] += new_element
                else:
                    date_format_parts.append(new_element)
            else:
                if new_element[0] in date_format_type_set:
                    msg = 'Multiple format specifiers for type %d' % new_element[0]
                    logging.getLogger(AminerConfig.DEBUG_LOG_NAME).error(msg)
                    raise ValueError(msg)
                date_format_type_set.add(new_element[0])
                date_format_parts.append(new_element)
            scan_pos = next_param_pos
        if (7 in date_format_type_set) and (not date_format_type_set.isdisjoint(set(range(0, 6)))):
            msg = 'Cannot use %s (seconds since epoch) with other non-second format types'
            logging.getLogger(AminerConfig.DEBUG_LOG_NAME).error(msg)
            raise ValueError(msg)
        self.date_format_parts = date_format_parts

    def get_id(self):
        """Get the element ID."""
        return self.path_id

    def get_child_elements(self):  # skipcq: PYL-R0201
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
        result = [0, 0, 0, 0, 0, 0, 0, 0]
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
        if total_seconds != 0:  # skipcq: PTC-W0048
            total_seconds += result[6]
        # For epoch second formats, the datetime value usually is not important. So stay with parsed_date_time to none.
        else:
            if not self.format_has_year_flag:
                result[0] = self.start_year
            microseconds = int(result[6] * 1000000)
            try:
                if 0 in (result[0], result[1], result[2]):
                    current_date = datetime.now()
                    if result[0] == 0:
                        result[0] = current_date.year
                    if result[1] == 0:
                        result[1] = current_date.month
                    if result[2] == 0:
                        result[2] = current_date.day
                parsed_date_time = datetime(result[0], result[1], result[2], result[3], result[4], result[5], microseconds,
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
                                datetime.fromtimestamp(self.last_parsed_seconds, self.time_zone).isoformat(),
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

        if self.format_has_tz_specifier:
            start = 0
            while start < parse_pos:
                try:
                    parse(match_context.match_data[start:parse_pos], tzinfos=timezone_info)
                    break
                # skipcq: FLK-E722
                except:
                    start += 1
            self.tz_specifier_format_length = len(match_context.match_data)
            # try to find the longest matching date
            while True:
                try:
                    parse(match_context.match_data[start:self.tz_specifier_format_length], tzinfos=timezone_info)
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
            self.tz_specifier_offset = 0
            self.tz_specifier_offset_str = remaining_data
            if b"+" not in remaining_data and b"-" not in remaining_data:
                offset = parse(date_str + remaining_data, tzinfos=timezone_info).utcoffset()
                if offset is not None:
                    self.tz_specifier_offset = -offset.days * 86400 - offset.seconds
            else:
                sign = -1
                data = remaining_data.split(b'+')
                if len(data) == 1:
                    data = remaining_data.split(b'-')
                    sign = 1
                    if len(data) == 1:
                        data = None
                # only add offset if a + or - sign is used.
                if data is not None:
                    if len(data) == 1:
                        data = remaining_data.split(b'-')
                    if len(data[1]) == 4:
                        self.tz_specifier_offset = (int(data[1][0:2]) * 3600 + int(data[1][2:4]) * 60) * sign
                    else:
                        self.tz_specifier_offset = (int(data[1])) * 3600 * sign
                    self.tz_specifier_offset_str = remaining_data
            total_seconds += self.tz_specifier_offset
            return MatchElement("%s/%s" % (path, self.path_id), date_str+remaining_data, total_seconds, None)
        return MatchElement("%s/%s" % (path, self.path_id), date_str, total_seconds, None)

    @staticmethod
    def parse_fraction(value_str):
        """Pass this method as function pointer to the parsing logic."""
        return float(b'0.' + value_str)


class MultiLocaleDateTimeModelElement(ModelElementInterface):
    """
    This class defines a model element to parse date or datetime values from log sources.
    The date or datetime can contain timestamps encoded in different locales or on machines, where host/service locale does not match data
    locale(s).
    CAVEAT: Unlike other model elements, this element is not completely stateless! As parsing of semiqualified date values without any
    year information may produce wrong results, e.g. wrong year or 1 day off due to incorrect leap year handling, this object
    will keep track of the most recent timestamp parsed and will use it to regain information about the year in semiqualified
    date values. Still this element will not complain when parsed timestamp values are not strictly sorted, this should be done
    by filtering modules later on. The sorting requirements here are only, that each new timestamp value may not be more than
    2 days before and 1 month after the most recent one observer.

    Internal operation:
    * When creating the object, make sure that there are no ambiguous dateFormats in the list, e.g. one with "day month" and another
    one with "month day".
    * To avoid decoding of binary input data in all locales before searching for e.g. month names, convert all possible month
    names to bytes during object creation and just keep the lookup list.
    """

    def __init__(self, path_id, date_formats, start_year=None, max_time_jump_seconds=86400):
        """
        Create a new MultiLocaleDateTimeModelElement object.
        @param date_formats this parameter is a list of tuples, each tuple containing information about one date format to support.
        The tuple structure is (format_string, format_locale, format_timezone). The format_string may contain the same elements as supported
        by strptime from datetime.datetime. The format_locale defines the locale for the string content, e.g. de_DE for german,
        but also the data IO encoding, e.g. ISO-8859-1. The locale information has to be available, e.g. using "locale-gen" on
        Debian systems. The format_timezone can be used to define the timezone of the timestamp parsed. When None, UTC is used.
        The timezone support may only be sufficient for very simple usecases, e.g. all data from one source configured to create
        timestamps in that timezone. This may still fail, e.g. when daylight savings changes make timestamps ambiguous during
        a short window of time. In all those cases, timezone should be left empty here and a separate filtering component should
        be used to apply timestamp corrections afterwards. See the
        FIXME-Filter component for that. Also having the same format_string for two different timezones
        will result in an error as correct timezone to apply cannot be distinguished just from format.
        @param start_year when given, parsing will use this year value for semiqualified timestamps to add correct year information.
        This is especially relevant for historic datasets as otherwise leap year handling may fail. The startYear parameter will
        only take effect when the first timestamp to be parsed by this object is also semiqualified. Otherwise the year information
        is extracted from this record. When empty and first parsing invocation involves a semiqualified date, the current year
        in UTC timezone is used.
        """
        if not isinstance(path_id, str):
            msg = "path_id has to be of the type string."
            logging.getLogger(AminerConfig.DEBUG_LOG_NAME).error(msg)
            raise TypeError(msg)
        if len(path_id) < 1:
            msg = "path_id must not be empty."
            logging.getLogger(AminerConfig.DEBUG_LOG_NAME).error(msg)
            raise ValueError(msg)
        self.path_id = path_id
        if len(date_formats) == 0:
            msg = "At least one date_format must be specified."
            logging.getLogger(AminerConfig.DEBUG_LOG_NAME).error(msg)
            raise ValueError(msg)

        if max_time_jump_seconds is not None and not isinstance(max_time_jump_seconds, int) or isinstance(max_time_jump_seconds, bool):
            msg = "max_time_jump_seconds has to be of the type integer."
            logging.getLogger(AminerConfig.DEBUG_LOG_NAME).error(msg)
            raise TypeError(msg)
        if max_time_jump_seconds <= 0:
            msg = "max_time_jump_seconds must not be lower than 1 second."
            logging.getLogger(AminerConfig.DEBUG_LOG_NAME).error(msg)
            raise ValueError(msg)
        self.max_time_jump_seconds = max_time_jump_seconds

        format_has_year_flag = False
        default_locale = locale.getdefaultlocale()
        self.date_time_model_elements = []
        for i, date_format in enumerate(date_formats):
            if not isinstance(date_format, tuple) or len(date_format) != 3:
                msg = "Invalid date_format. Must be tuple with 3 elements."
                logging.getLogger(AminerConfig.DEBUG_LOG_NAME).error(msg)
                raise ValueError(msg)
            date_format, time_zone, text_locale = date_format
            for date_time_model_element in self.date_time_model_elements:
                if date_format.startswith(date_time_model_element.date_format):
                    msg = "Invalid order of date_formats. %s starts with %s. More specific datetimes would be skipped." % (
                        date_format.decode(), date_time_model_element.date_format.decode())
                    logging.getLogger(AminerConfig.DEBUG_LOG_NAME).error(msg)
                    raise ValueError(msg)
            self.date_time_model_elements.append(DateTimeModelElement(
                path_id + "/format" + str(i), date_format, time_zone, text_locale, start_year, max_time_jump_seconds))
            format_has_year_flag = format_has_year_flag and self.date_time_model_elements[-1].format_has_year_flag

        # The latest parsed timestamp value.
        self.latest_parsed_timestamp = None

        # Restore previous locale settings. There seems to be no way in python to get back to the exact same state. Hence perform the
        # reset only when locale has changed. This would also change the locale from (None, None) to some system-dependent locale.
        if locale.getlocale() != default_locale:
            locale.resetlocale()

        if start_year is not None and not isinstance(start_year, int) or isinstance(start_year, bool):
            msg = "start_year has to be of the type integer."
            logging.getLogger(AminerConfig.DEBUG_LOG_NAME).error(msg)
            raise TypeError(msg)
        self.start_year = start_year
        if (not format_has_year_flag) and (start_year is None):
            self.start_year = time.gmtime(None).tm_year
        self.last_parsed_seconds = 0

    def get_id(self):
        """Get the element ID."""
        return self.path_id

    def get_child_elements(self):  # skipcq: PYL-R0201
        """
        Get all possible child model elements of this element.
        @return empty list as there are no children of this element.
        """
        return None

    def get_match_element(self, path, match_context):
        """
        Check if the data to match within the content is suitable to be parsed by any of the supplied date formats.
        @return On match return a matchObject containing a tuple of the datetime object and the seconds since 1970. When not matching,
        None is returned. When the timestamp data parsed would be far off from the last ones parsed, so that correction may
        not be applied correctly, then the method will also return None.
        """
        for i, date_time_model_element in enumerate(self.date_time_model_elements):
            locale.setlocale(locale.LC_ALL, date_time_model_element.text_locale)
            self.date_time_model_elements[i].last_parsed_seconds = self.last_parsed_seconds
            self.date_time_model_elements[i].start_year = self.start_year
            try:
                match_element = date_time_model_element.get_match_element(path, match_context)
                if match_element is not None:
                    self.last_parsed_seconds = date_time_model_element.last_parsed_seconds
                    self.start_year = date_time_model_element.start_year
                    return match_element
            except:  # skipcq: FLK-E722
                pass
        return None
