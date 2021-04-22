"""
This module defines a model element that represents an IP address.

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
import re
from aminer.AminerConfig import DEBUG_LOG_NAME
from aminer.parsing.MatchElement import MatchElement
from aminer.parsing.ModelElementInterface import ModelElementInterface


class IpAddressDataModelElement(ModelElementInterface):
    """This class defines a model element that matches an IP address."""

    def __init__(self, element_id: str, ipv6: bool = False):
        """Create an element to match IP addresses."""
        if not isinstance(element_id, str):
            msg = "element_id has to be of the type string."
            logging.getLogger(DEBUG_LOG_NAME).error(msg)
            raise TypeError(msg)
        if len(element_id) < 1:
            msg = "element_id must not be empty."
            logging.getLogger(DEBUG_LOG_NAME).error(msg)
            raise ValueError(msg)
        self.element_id = element_id

        if not isinstance(ipv6, bool):
            msg = "ipv6 has to be of the type bool."
            logging.getLogger(DEBUG_LOG_NAME).error(msg)
            raise TypeError(msg)
        if not ipv6:
            # self.regex = re.compile(br"((2[0-4][0-9]|1[0-9][0-9]|25[0-5]|[1-9]?[0-9])\.){3}(2[0-4][0-9]|1[0-9][0-9]|25[0-5]|[1-9]?[0-9])")
            # use a simpler regex to improve the performance.
            self.regex = re.compile(br"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}")
            self.extract = extract_ipv4_address
        else:
            # modified regex from https://community.helpsystems.com/forums/intermapper/miscellaneous-topics/
            # 5acc4fcf-fa83-e511-80cf-0050568460e4?_ga=2.113564423.1432958022.1523882681-2146416484.1523557976
            i4 = br"((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3})"
            self.regex = re.compile(
                br"((([0-9A-Fa-f]{1,4}:){7}([0-9A-Fa-f]{1,4}|:))|(([0-9A-Fa-f]{1,4}:){6}(:[0-9A-Fa-f]{1,4}|"+i4+br"|:))|(([0-9A-Fa-f]{1,4}:"
                br"){5}(((:[0-9A-Fa-f]{1,4}){1,2})|:"+i4+br"|:))|(([0-9A-Fa-f]{1,4}:){4}(((:[0-9A-Fa-f]{1,4}){1,3})|((:[0-9A-Fa-f]{1,4})?"
                br":"+i4+br")|:))|(([0-9A-Fa-f]{1,4}:){3}(((:[0-9A-Fa-f]{1,4}){1,4})|((:[0-9A-Fa-f]{1,4}){0,2}:"+i4+br")|:))|(([0-9A-Fa-f]{"
                br"1,4}:){2}(((:[0-9A-Fa-f]{1,4}){1,5})|((:[0-9A-Fa-f]{1,4}){0,3}:"+i4+br")|:))|(([0-9A-Fa-f]{1,4}:){1}(((:[0-9A-Fa-f]{"
                br"1,4}){1,6})|((:[0-9A-Fa-f]{1,4}){0,4}:"+i4+br")|:))|(:(((:[0-9A-Fa-f]{1,4}){1,7})|((:[0-9A-Fa-f]{1,4}){0,5}:"+i4+br")|:"
                br")))(%.+)?")
            self.extract = extract_ipv6_address

    def get_id(self):
        """Get the element ID."""
        return self.element_id

    def get_child_elements(self):  # skipcq: PYL-R0201
        """
        Get all possible child model elements of this element.
        @return None as there are no children of this element.
        """
        return None

    def get_match_element(self, path: str, match_context):
        """Read an IP address at the current data position. When found, the match_object will be."""
        #create variable for match_context.match_data!!
        m = self.regex.match(match_context.match_data)
        print(m)
        if m is None:
            return None
        match_len = m.span(0)[1]
        #last one does not work yet..
        if self.extract == extract_ipv6_address and (b"." in m.group()[:match_len].split(b":")[-1] or (len(
                match_context.match_data) > match_len and (match_context.match_data[match_len] == ord(b".") or match_context.match_data[match_len] == ord(b":")))):
            return None
        extracted_address = self.extract(m.group(), match_len)
        if extracted_address is None:
            return None
        match_string = match_context.match_data[:match_len]
        match_context.update(match_string)
        return MatchElement("%s/%s" % (path, self.element_id), match_string, extracted_address, None)


def extract_ipv4_address(data: bytes, match_len: int):
    numbers = data[:match_len].split(b".")
    numbers = [int(number) for number in numbers]
    for number in numbers:
        if number > 255:
            return None
    return (numbers[0] << 24) + (numbers[1] << 16) + (numbers[2] << 8) + numbers[3]


def extract_ipv6_address(data: bytes, match_len: int):
    numbers = data[:match_len].split(b":")
    print(numbers)
    # if b"" in numbers[-1]:
    #     return None
    if b"" in numbers:
        index = numbers.index(b"")
        # addresses can start or end with ::. Handle this special case.
        numbers = [number for number in numbers if number != b""]
        numbers = numbers[:index] + [b"0"] * (8 - len(numbers)) + numbers[index:]
    numbers = [int(b"0x" + number, 16) for number in numbers]
    for number in numbers:
        if number > 65535:
            return None
    return (numbers[0] << 112) + (numbers[1] << 96) + (numbers[2] << 80) + (numbers[3] << 64) + (numbers[4] << 48) + (numbers[5] << 32)\
        + (numbers[6] << 16) + (numbers[7])
