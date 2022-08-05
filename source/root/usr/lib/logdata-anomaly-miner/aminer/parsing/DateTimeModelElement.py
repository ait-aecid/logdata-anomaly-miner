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
from typing import Union, List, Set
from datetime import timezone, datetime

from aminer.AminerConfig import DEBUG_LOG_NAME
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

search_tz_dict = {}
keys = list(timezone_info.keys())
keys.sort()
for idx in range(65, 91):
    search_tz_dict[idx] = [x.encode() for x in keys if x.encode()[0] == idx]
    search_tz_dict[idx].sort(key=len, reverse=True)  # sorts by descending length


class DateTimeModelElement(ModelElementInterface):
    """
    This class defines a model element to parse date or datetime values.
    The element is similar to the strptime function but does not use it due to the numerous problems associated with it, e.g. no leap year
    support for semiqualified years, no %s (seconds since epoch) format in Python strptime, no %f support in libc strptime, no support to
    determine the length of the parsed string.
    """

    # skipcq: PYL-W0613
    def __init__(self, element_id: str, date_format: bytes, time_zone: timezone = None, text_locale: Union[str, tuple] = None,
                 start_year: int = None, max_time_jump_seconds: int = 86400):
        """
        Create a DateTimeModelElement to parse dates using a custom, timezone and locale-aware implementation similar to strptime.
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
        """
        self.text_locale = text_locale
        super().__init__(element_id, date_format=date_format, time_zone=time_zone, text_locale=text_locale, start_year=start_year,
                         max_time_jump_seconds=max_time_jump_seconds)
        if time_zone is None:
            self.time_zone = timezone.utc
        # Make sure that date_format is valid and extract the relevant parts from it.
        self.format_has_year_flag = False
        self.format_has_tz_specifier = False
        self.date_format_parts: Union[List[Union[bytes, tuple]]] = []
        self.scan_date_format(date_format)

        if (not self.format_has_year_flag) and (start_year is None):
            self.start_year = time.gmtime(None).tm_year
        elif start_year is None:  # this is needed so start_year is at any point an integer. (instead of being None)
            self.start_year = 0

        self.last_parsed_seconds = 0
        self.epoch_start_time = datetime.fromtimestamp(0, self.time_zone)

    def scan_date_format(self, date_format: bytes):
        """Scan the date format."""
        if len(self.date_format_parts) > 0:
            msg = "Cannot rescan date format after initialization"
            logging.getLogger(DEBUG_LOG_NAME).error(msg)
            raise Exception(msg)
        date_format_parts: List[Union[bytes, tuple]] = []
        date_format_type_set: Set[int] = set()
        scan_pos = 0
        while scan_pos < len(date_format):
            next_param_pos = date_format.find(b"%", scan_pos)
            if next_param_pos < 0:
                next_param_pos = len(date_format)
            new_element: Union[bytes, tuple, None] = None
            if next_param_pos != scan_pos:
                new_element = date_format[scan_pos:next_param_pos]
            else:
                param_type_code = date_format[next_param_pos + 1:next_param_pos + 2]
                next_param_pos = scan_pos + 2
                if param_type_code == b"%":
                    new_element = b"%"
                elif param_type_code == b"b":
                    import calendar
                    name_dict = {}
                    for month_pos in range(1, 13):
                        name_dict[calendar.month_name[month_pos][:3].encode()] = month_pos
                    new_element = (1, 3, name_dict)
                elif param_type_code == b"d":
                    new_element = (2, 2, int)
                elif param_type_code == b"f":
                    new_element = (6, -1, DateTimeModelElement.parse_fraction)
                elif param_type_code == b"H":
                    new_element = (3, 2, int)
                elif param_type_code == b"M":
                    new_element = (4, 2, int)
                elif param_type_code == b"m":
                    new_element = (1, 2, int)
                elif param_type_code == b"S":
                    new_element = (5, 2, int)
                elif param_type_code == b"s":
                    new_element = (7, -1, int)
                elif param_type_code == b"Y":
                    self.format_has_year_flag = True
                    new_element = (0, 4, int)
                elif param_type_code == b"z":
                    self.format_has_tz_specifier = True
                    scan_pos = next_param_pos
                    continue
                else:
                    msg = f"Unknown dateformat specifier {repr(param_type_code)}"
                    logging.getLogger(DEBUG_LOG_NAME).error(msg)
                    raise ValueError(msg)
            if isinstance(new_element, bytes):
                if date_format_parts and (isinstance(date_format_parts[-1], bytes)):
                    date_format_parts[-1] += new_element
                else:
                    date_format_parts.append(new_element)
            else:
                if new_element[0] in date_format_type_set:
                    msg = f"Multiple format specifiers for type {new_element[0]}"
                    logging.getLogger(DEBUG_LOG_NAME).error(msg)
                    raise ValueError(msg)
                date_format_type_set.add(new_element[0])
                date_format_parts.append(new_element)
            scan_pos = next_param_pos
        if (7 in date_format_type_set) and (not date_format_type_set.isdisjoint(set(range(0, 6)))):
            msg = f"Cannot use %s (seconds since epoch) with other non-second format types"
            logging.getLogger(DEBUG_LOG_NAME).error(msg)
            raise ValueError(msg)
        self.date_format_parts = date_format_parts

    def get_match_element(self, path: str, match_context):
        """
        Try to find a match on given data for this model element and all its children.
        When a match is found, the match_context is updated accordingly.
        @param path to be printed in the MatchElement.
        @param match_context the match_context to be analyzed.
        @return None when there is no match, MatchElement otherwise. The match_object returned is a tuple containing the datetime
                object and the seconds since 1970.
        """
        parse_pos = 0
        # Year, month, day, hour, minute, second, fraction, gmt-seconds:
        result: List = [0, 0, 0, 0, 0, 0, 0, 0]
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
                    delta_seconds = self.last_parsed_seconds - total_seconds
                    if abs(delta_seconds) <= self.max_time_jump_seconds:
                        self.last_parsed_seconds = total_seconds
                    else:
                        # This might be the first date value for the next year or one from the previous.
                        # Test both cases and see, what is more likely.
                        date_error = False
                        try:
                            next_year_date_time = parsed_date_time.replace(self.start_year + 1)
                            delta = next_year_date_time - self.epoch_start_time
                            next_year_total_seconds = (delta.days * 86400 + delta.seconds)
                        except ValueError:
                            date_error = True
                        if not date_error and next_year_total_seconds - self.last_parsed_seconds <= self.max_time_jump_seconds:
                            self.start_year += 1
                            parsed_date_time = next_year_date_time
                            total_seconds = next_year_total_seconds
                            self.last_parsed_seconds = total_seconds
                            msg = f"DateTimeModelElement unqualified timestamp year wraparound detected from " \
                                  f"{datetime.fromtimestamp(self.last_parsed_seconds, self.time_zone).isoformat()} to " \
                                  f"{parsed_date_time.isoformat()}"
                            logging.getLogger(DEBUG_LOG_NAME).warning(msg)
                            print("WARNING: " + msg, file=sys.stderr)
                        else:
                            try:
                                last_year_date_time = parsed_date_time.replace(self.start_year - 1)
                                delta = last_year_date_time - self.epoch_start_time
                                last_year_total_seconds = (delta.days * 86400 + delta.seconds)
                            except ValueError:
                                date_error = True
                            if not date_error and self.last_parsed_seconds - last_year_total_seconds <= self.max_time_jump_seconds:
                                parsed_date_time = last_year_date_time
                                total_seconds = last_year_total_seconds
                                self.last_parsed_seconds = total_seconds
                            else:
                                # None of both seems correct, just report that.
                                msg = f"DateTimeModelElement time inconsistencies parsing {repr(date_str)}, expecting value around " \
                                      f"{self.last_parsed_seconds}. Check your settings!"
                                logging.getLogger(DEBUG_LOG_NAME).warning(msg)
                                print("WARNING: " + msg, file=sys.stderr)

            # We discarded the parsed_date_time microseconds beforehand, use the full float value here instead of the rounded integer.
            if result[6] is not None:
                total_seconds += result[6]

        if self.format_has_tz_specifier:
            valid_tz_specifier = True
            offset_allowed = True
            tz_specifier_offset = 0.
            if match_context.match_data[parse_pos] == ord(b" "):
                parse_pos += 1
                resulting_key = None
                # only if the next character is in A-Z, a valid resulting_key can exist.
                if match_context.match_data[parse_pos] in search_tz_dict:
                    # search the first fitting resulting_key in the sorted tz_dict and break the loop.
                    for key in search_tz_dict[match_context.match_data[parse_pos]]:
                        if match_context.match_data[parse_pos:].startswith(key):
                            resulting_key = key
                            break
                    # an offset is only allowed with UTC and GMT.
                    if resulting_key not in (b"UTC", b"GMT"):
                        offset_allowed = False
                    if resulting_key is not None:
                        # get the offset from the timezone_info dict.
                        tz_specifier_offset = timezone_info[resulting_key.decode()]
                        parse_pos += len(resulting_key)

            if match_context.match_data[parse_pos] in (ord(b"+"), ord(b"-")) and offset_allowed and valid_tz_specifier:
                sign = -1
                if match_context.match_data[parse_pos] == ord(b"+"):
                    sign = 1
                parse_pos += 1
                cnt_digits = 0
                colon_shift = 0
                # parse data as long as there is more data.
                while parse_pos < len(match_context.match_data):
                    # shift the position and count to the next position, if the current character is a digit.
                    if chr(match_context.match_data[parse_pos]).isdigit():
                        cnt_digits += 1
                        parse_pos += 1
                    # if the current character is no digit and cnt_digits is 2, a colon is allowed.
                    elif cnt_digits == 2 and match_context.match_data[parse_pos] == ord(b":"):
                        parse_pos += 1
                        colon_shift = 1
                    else:
                        break
                # if the digit count is not 4 and a colon is found, then no colon shift should be applied. This could be the case, if a
                # colon follows the date (02.11.2021 UTC+01: some text)
                if cnt_digits != 4 and colon_shift == 1:
                    parse_pos -= 1
                    colon_shift = 0
                # if the digits count is zero or bigger than 4, then the specifier is not valid.
                if cnt_digits == 0 or cnt_digits > 4:
                    valid_tz_specifier = False
                else:
                    # only one hour position was found.
                    if cnt_digits == 1:
                        tz_specifier_offset = sign * int(chr(match_context.match_data[parse_pos-1])) * 3600
                    # two hours specifiers were found.
                    elif cnt_digits == 2:
                        tz_specifier_offset = sign * int(match_context.match_data[parse_pos-2:parse_pos].decode()) * 3600
                    # four time specifiers were found with an optional colon.
                    elif cnt_digits == 4:
                        tz_specifier_offset = sign * int(match_context.match_data[parse_pos-4-colon_shift:parse_pos-2-colon_shift]) * \
                                              3600 + int(match_context.match_data[parse_pos-2:parse_pos] * 60)

            if valid_tz_specifier:
                date_str = match_context.match_data[:parse_pos]
                # the offset must be subtracted, because the timestamp should always be UTC.
                total_seconds -= tz_specifier_offset
        match_context.update(date_str)
        return MatchElement(f"{path}/{self.element_id}", date_str, total_seconds, None)

    @staticmethod
    def parse_fraction(value_str: bytes):
        """Pass this method as function pointer to the parsing logic."""
        return float(b"0." + value_str)


class MultiLocaleDateTimeModelElement(ModelElementInterface):
    """
    This class defines a model element to parse date or datetime values from log sources.
    The date or datetime can contain timestamps encoded in different locales or on machines, where host/service locale does not match data
    locale(s).
    CAVEAT: Unlike other model elements, this element is not completely stateless! As parsing of semi qualified date values without any
    year information may produce wrong results, e.g. wrong year or 1 day off due to incorrect leap year handling, this object
    will keep track of the most recent timestamp parsed and will use it to regain information about the year in semi qualified
    date values. Still this element will not complain when parsed timestamp values are not strictly sorted, this should be done
    by filtering modules later on. The sorting requirements here are only, that each new timestamp value may not be more than
    2 days before and 1 month after the most recent one observer.

    Internal operation:
    * When creating the object, make sure that there are no ambiguous dateFormats in the list, e.g. one with "day month" and another
    one with "month day".
    * To avoid decoding of binary input data in all locales before searching for e.g. month names, convert all possible month
    names to bytes during object creation and just keep the lookup list.
    """

    def __init__(self, element_id: str, date_formats: list, start_year: int = None, max_time_jump_seconds: int = 86400):
        """
        Create a new MultiLocaleDateTimeModelElement object.
        @param element_id an identifier for the ModelElement which is shown in the path.
        @param date_formats this parameter is a list of tuples, each tuple containing information about one date format to support.
               The tuple structure is (format_string, format_timezone, format_locale). The format_string may contain the same elements as
               supported by strptime from datetime.datetime. The format_locale defines the locale for the string content, e.g. de_DE for
               german, but also the data IO encoding, e.g. ISO-8859-1. The locale information has to be available, e.g. using "locale-gen"
               on Debian systems. The format_timezone can be used to define the timezone of the timestamp parsed. When None, UTC is used.
               The timezone support may only be sufficient for very simple use-cases, e.g. all data from one source configured to create
               timestamps in that timezone.
        @param start_year when given, parsing will use this year value for semi qualified timestamps to add correct year information.
               This is especially relevant for historic datasets as otherwise leap year handling may fail. The startYear parameter will
               only take effect when the first timestamp to be parsed by this object is also semi qualified. Otherwise, the year information
               is extracted from this record. When empty and first parsing invocation involves a semi qualified date, the current year
               in UTC timezone is used.
        @param max_time_jump_seconds for detection of year wraps with date formats missing year information, also the current time
               of values has to be tracked. This value defines the window within that the time may jump between two matches. When not
               within that window, the value is still parsed, corrected to the most likely value but does not change the detection year.
        """
        super().__init__(element_id, start_year=start_year, max_time_jump_seconds=max_time_jump_seconds)
        if len(date_formats) == 0:
            msg = "At least one date_format must be specified."
            logging.getLogger(DEBUG_LOG_NAME).error(msg)
            raise ValueError(msg)

        format_has_year_flag = False
        default_locale = locale.getdefaultlocale()
        self.date_time_model_elements: List[DateTimeModelElement] = []
        for i, date_format in enumerate(date_formats):
            if not isinstance(date_format, tuple):
                msg = "date_format must be of type tuple."
                logging.getLogger(DEBUG_LOG_NAME).error(msg)
                raise TypeError(msg)
            if len(date_format) != 3:
                msg = "date_format consist of 3 elements."
                logging.getLogger(DEBUG_LOG_NAME).error(msg)
                raise ValueError(msg)
            date_format, time_zone, text_locale = date_format
            if isinstance(text_locale, str) and len(text_locale) < 1:
                msg = "empty text_locale is not allowed."
                logging.getLogger(DEBUG_LOG_NAME).error(msg)
                raise ValueError(msg)
            for date_time_model_element in self.date_time_model_elements:
                if date_format.startswith(date_time_model_element.date_format):
                    msg = f"Invalid order of date_formats. {date_format.decode()} starts with " \
                          f"{date_time_model_element.date_format.decode()}. More specific datetimes would be skipped."
                    logging.getLogger(DEBUG_LOG_NAME).error(msg)
                    raise ValueError(msg)
            self.date_time_model_elements.append(DateTimeModelElement(
                element_id + "/format" + str(i), date_format, time_zone, text_locale, start_year, max_time_jump_seconds))
            format_has_year_flag = format_has_year_flag and self.date_time_model_elements[-1].format_has_year_flag

        # The latest parsed timestamp value.
        self.latest_parsed_timestamp = None

        # Restore previous locale settings. There seems to be no way in python to get back to the exact same state. Hence perform the
        # reset only when locale has changed. This would also change the locale from (None, None) to some system-dependent locale.
        if locale.getlocale() != default_locale:
            locale.resetlocale()

        if (not format_has_year_flag) and (start_year is None):
            self.start_year = time.gmtime(None).tm_year
        elif start_year is None:   # this is needed so start_year is at any point an integer. (instead of being None)
            self.start_year = 0
        self.last_parsed_seconds = 0

    def get_match_element(self, path: str, match_context):
        """
        Check if the data to match within the content is suitable to be parsed by any of the supplied date formats.
        @param path to be printed in the MatchElement.
        @param match_context the match_context to be analyzed.
        @return On match return a match_object containing a tuple of the datetime object and the seconds since 1970. When not matching,
                None is returned. When the timestamp data parsed would be far off from the last ones parsed, so that correction may
                not be applied correctly, then the method will also return None.
        """
        for i, date_time_model_element in enumerate(self.date_time_model_elements):
            locale.setlocale(locale.LC_ALL, date_time_model_element.text_locale)
            self.date_time_model_elements[i].last_parsed_seconds = self.last_parsed_seconds
            self.date_time_model_elements[i].start_year = self.start_year
            match_element = date_time_model_element.get_match_element(path, match_context)
            if match_element is not None:
                self.last_parsed_seconds = date_time_model_element.last_parsed_seconds
                self.start_year = date_time_model_element.start_year
                return match_element
        return None
