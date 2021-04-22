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
    """This class defines a model element that matches an IPv4 IP address."""

    def __init__(self, element_id: str):
        """Create an element to match IPv4 IP addresses."""
        if not isinstance(element_id, str):
            msg = "element_id has to be of the type string."
            logging.getLogger(DEBUG_LOG_NAME).error(msg)
            raise TypeError(msg)
        if len(element_id) < 1:
            msg = "element_id must not be empty."
            logging.getLogger(DEBUG_LOG_NAME).error(msg)
            raise ValueError(msg)
        self.element_id = element_id
        # self.regex = re.compile(br"((2[0-4][0-9]|1[0-9][0-9]|25[0-5]|[1-9]?[0-9])\.){3}(2[0-4][0-9]|1[0-9][0-9]|25[0-5]|[1-9]?[0-9])")
        # use a simpler regex to improve the performance.
        self.regex = re.compile(br"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}")

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
        m = self.regex.match(match_context.match_data)
        if m is None:
            return None
        match_len = m.span(0)[1]
        data = match_context.match_data
        numbers = data[:match_len].split(b".")
        numbers = [int(number) for number in numbers]
        for number in numbers:
            if number > 255:
                return None
        extracted_address = (numbers[0] << 24) + (numbers[1] << 16) + (numbers[2] << 8) + numbers[3]
        match_string = data[:match_len]
        match_context.update(match_string)
        return MatchElement("%s/%s" % (path, self.element_id), match_string, extracted_address, None)
