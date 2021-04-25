"""
This module defines a model element that is optional.

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


class OptionalMatchModelElement(ModelElementInterface):
    """
    This class defines a model element tries to match against a given model element.
    If that fails returns a zero length match anyway.
    """

    def __init__(self, element_id: str, optional_element: ModelElementInterface):
        if not isinstance(element_id, str):
            msg = "element_id has to be of the type string."
            logging.getLogger(DEBUG_LOG_NAME).error(msg)
            raise TypeError(msg)
        if len(element_id) < 1:
            msg = "element_id must not be empty."
            logging.getLogger(DEBUG_LOG_NAME).error(msg)
            raise ValueError(msg)
        self.element_id = element_id

        if not isinstance(optional_element, ModelElementInterface):
            msg = "optional_element has to be of the type ModelElementInterface."
            logging.getLogger(DEBUG_LOG_NAME).error(msg)
            raise TypeError(msg)
        self.optional_element = optional_element
        self.empty_match_element = MatchElement("%s/%s" % ("None", self.element_id), b"None", None, None)
        self.empty_match_element.match_string = b""

    def get_id(self):
        """Get the element ID."""
        return self.element_id

    def get_child_elements(self):
        """Return all optional elements."""
        return [self.optional_element]

    def get_match_element(self, path: str, match_context):
        """@return the embedded child match or an empty match."""
        current_path = "%s/%s" % (path, self.element_id)

        start_data = match_context.match_data
        match = self.optional_element.get_match_element(current_path, match_context)
        if match is None:
            self.empty_match_element.path = current_path
            return self.empty_match_element

        return MatchElement(current_path, start_data[:len(start_data) - len(match_context.match_data)],
                            start_data[:len(start_data) - len(match_context.match_data)], [match])
