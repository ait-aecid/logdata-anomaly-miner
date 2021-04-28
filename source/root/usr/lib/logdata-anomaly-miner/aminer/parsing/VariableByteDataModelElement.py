"""
This module defines a model element for a variable amount of bytes.

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
from aminer.AminerConfig import DEBUG_LOG_NAME
from aminer.parsing.MatchElement import MatchElement
from aminer.parsing.ModelElementInterface import ModelElementInterface


class VariableByteDataModelElement(ModelElementInterface):
    """This class defines a model element  that takes any string that only contains characters of a given alphabet."""

    def __init__(self, element_id: str, alphabet: bytes):
        if not isinstance(element_id, str):
            msg = "element_id has to be of the type string."
            logging.getLogger(DEBUG_LOG_NAME).error(msg)
            raise TypeError(msg)
        if len(element_id) < 1:
            msg = "element_id must not be empty."
            logging.getLogger(DEBUG_LOG_NAME).error(msg)
            raise ValueError(msg)
        self.element_id = element_id

        if not isinstance(alphabet, bytes):
            msg = "alphabet has to be of the type bytes."
            logging.getLogger(DEBUG_LOG_NAME).error(msg)
            raise TypeError(msg)
        if len(alphabet) < 1:
            msg = "alphabet must not be empty."
            logging.getLogger(DEBUG_LOG_NAME).error(msg)
            raise ValueError(msg)
        self.alphabet = alphabet

    def get_id(self):
        """Get the element ID."""
        return self.element_id

    def get_child_elements(self):  # skipcq: PYL-R0201
        """
        Get all possible child model elements of this element.
        @return None as there are no children of this element.
        """
        return None

    def get_match_element(self, path, match_context):
        """
        Find the maximum number of bytes matching the given alphabet.
        @return a match when at least one byte was found within alphabet.
        """
        data = match_context.match_data
        match_len = 0
        for test_byte in data:
            if test_byte not in self.alphabet:
                break
            match_len += 1

        if match_len == 0:
            return None
        match_data = data[:match_len]
        match_context.update(match_data)
        return MatchElement("%s/%s" % (path, self.element_id), match_data, match_data, None)
