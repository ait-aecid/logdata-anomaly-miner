"""
This module provides base64 string matching.

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
import base64
import logging
import re
from aminer import AminerConfig
from aminer.parsing.ModelElementInterface import ModelElementInterface
from aminer.parsing.MatchElement import MatchElement


class Base64StringModelElement(ModelElementInterface):
    """This class just tries to strip off as many base64 bytes as possible from a given data string."""

    def __init__(self, path_id):
        if not isinstance(path_id, str) or len(path_id) < 1:
            msg = "element_id has to be of the type string and must not be empty."
            logging.getLogger(AminerConfig.DEBUG_LOG_NAME).error(msg)
            raise ValueError(msg)
        self.path_id = path_id
        self.regex = re.compile(b"^(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?")

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
        Find the maximum number of bytes forming a integer number according to the parameters specified.
        @return a match when at least one byte being a digit was found.
        """
        match = self.regex.match(match_context.match_data)
        if match is None or match.span()[1] == 0:
            return None
        match_len = match.span()[1]

        match_string = match_context.match_data[:match_len]
        match_context.update(match_string)
        try:
            match_value = base64.b64decode(match_string)
            # we need to check if no exception is raised when decoding the original string.
            match_value.decode()
        except UnicodeDecodeError:
            match_value = match_string
        return MatchElement("%s/%s" % (path, self.path_id), match_string, match_value, None)
