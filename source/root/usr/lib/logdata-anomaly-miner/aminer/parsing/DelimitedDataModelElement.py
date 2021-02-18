"""
This module defines a model element that takes any string up to a specific delimiter string.

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
from aminer.parsing.ModelElementInterface import ModelElementInterface
import re


class DelimitedDataModelElement(ModelElementInterface):
    """Find a string delimited by given non-escaped delimiter string, possibly a match of zero byte length."""

    def __init__(self, element_id, delimiter, escape=None, consume_delimiter=False):
        self.element_id = element_id
        self.delimiter = delimiter
        if isinstance(escape, bytes):
            escape = escape.decode()
        self.escape = escape
        self.consume_delimiter = consume_delimiter

    def get_id(self):
        """Get the element ID."""
        return self.element_id

    # skipcq: PYL-R0201
    def get_child_elements(self):
        """
        Get all possible child model elements of this element.
        @return None as there are no children of this element.
        """
        return None

    def get_match_element(self, path, match_context):
        """
        Find the maximum number of bytes before encountering the non-escaped delimiter.
        @return a match when at least one byte was found but not the delimiter itself.
        """
        data = match_context.match_data
        match_len = -1
        if self.escape is None:
            search = re.search(re.escape(self.delimiter), data)
            if search is not None:
                match_len = search.start()
        else:
            search = re.search(rb'(?<!' + re.escape(self.escape).encode() + rb')' + re.escape(self.delimiter), data)
            if search is not None:
                match_len = search.start()
        if match_len < 1:
            return None
        match_data = data[:match_len + len(self.delimiter) * (self.consume_delimiter is True)]
        match_context.update(match_data)
        return MatchElement("%s/%s" % (path, self.element_id), match_data, match_data, None)
