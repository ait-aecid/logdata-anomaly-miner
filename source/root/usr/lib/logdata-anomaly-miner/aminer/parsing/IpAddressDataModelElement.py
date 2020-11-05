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


from aminer.parsing.MatchElement import MatchElement
from aminer.parsing import ModelElementInterface


class IpAddressDataModelElement(ModelElementInterface):
    """This class defines a model element that matches an IPv4 IP address."""

    def __init__(self, element_id):
        """Create an element to match IPv4 IP addresses."""
        self.element_id = element_id

    def get_id(self):
        """Get the element ID."""
        return self.element_id

    def get_child_elements(self):
        """
        Get all possible child model elements of this element.
        @return None as there are no children of this element.
        """
        return None

    def get_match_element(self, path, match_context):
        """Read an IP address at the current data position. When found, the matchObject will be."""
        data = match_context.match_data

        number_count = 0
        digit_count = 0
        match_len = 0
        extracted_address = 0
        for test_byte in data:
            match_len += 1
            if test_byte in b'0123456789':
                digit_count += 1
                continue
            if digit_count == 0:
                return None

            ip_bits = int(data[match_len - digit_count - 1:match_len - 1])
            if ip_bits > 0xff:
                return None
            extracted_address = (extracted_address << 8) | ip_bits
            digit_count = 0
            number_count += 1
            if number_count == 4:
                # We are now after the first byte not belonging to the IP. So go back one step
                match_len -= 1
                break
            if test_byte != ord(b'.'):
                return None

        if digit_count != 0:
            ip_bits = int(data[match_len - digit_count:match_len])
            if ip_bits > 0xff:
                return None
            extracted_address = (extracted_address << 8) | ip_bits

        match_string = data[:match_len]
        match_context.update(match_string)
        return MatchElement("%s/%s" % (path, self.element_id), match_string, extracted_address, None)
