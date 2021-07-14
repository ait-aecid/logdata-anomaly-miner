"""
This module defines a model element that represents a hex string of arbitrary length.

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
from aminer import AminerConfig


class HexStringModelElement(ModelElementInterface):
    """This class just tries to strip off as many hex bytes as possible from a given data string."""

    def __init__(self, element_id: str, upper_case: bool = False):
        if not isinstance(element_id, str):
            msg = "element_id has to be of the type string."
            logging.getLogger(DEBUG_LOG_NAME).error(msg)
            raise TypeError(msg)
        if len(element_id) < 1:
            msg = "element_id must not be empty."
            logging.getLogger(DEBUG_LOG_NAME).error(msg)
            raise ValueError(msg)
        self.element_id = element_id

        if not isinstance(upper_case, bool):
            msg = "upper_case has to be of the type bool."
            logging.getLogger(DEBUG_LOG_NAME).error(msg)
            raise TypeError(msg)
        if upper_case:
            self.hex_regex = re.compile(rb"[0-9A-F]+")
        else:
            self.hex_regex = re.compile(rb"[0-9a-f]+")

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
        """
        Find the maximum number of bytes forming a integer number according to the parameters specified.
        @return a match when at least one byte being a digit was found
        """
        m = self.hex_regex.match(match_context.match_data)
        if m is None:
            return None
        match_len = m.span(0)[1]

        match_object = match_context.match_data[:match_len]
        try:
            pad = ""
            if len(match_object.decode(AminerConfig.ENCODING)) % 2 != 0:
                pad = "0"
            match_string = bytes.fromhex(pad + match_object.decode(AminerConfig.ENCODING))
        except ValueError:
            return None
        match_context.update(match_object)
        return MatchElement("%s/%s" % (path, self.element_id), match_string, match_object, None)
