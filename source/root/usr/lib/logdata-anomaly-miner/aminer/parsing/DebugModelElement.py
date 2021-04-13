"""
This module defines a debug model element that can be used to check whether a specific position in the parsing tree is reached by log atoms.

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
import logging
from aminer.AminerConfig import DEBUG_LOG_NAME
from aminer.parsing.MatchElement import MatchElement
from aminer.parsing.ModelElementInterface import ModelElementInterface


class DebugModelElement(ModelElementInterface):
    """
    This class defines a model element matching any data of length zero at any position.
    Thus it can never fail to match and can be inserted at any position in the parsing tree, where matching itself does not alter parsing
    flow (see e.g. FirstMatchModelElement). It will immediately write the current state of the match to stderr for inspection.
    """

    def __init__(self, element_id):
        if not isinstance(element_id, str):
            msg = "element_id has to be of the type string."
            logging.getLogger(DEBUG_LOG_NAME).error(msg)
            raise TypeError(msg)
        if len(element_id) < 1:
            msg = "element_id must not be empty."
            logging.getLogger(DEBUG_LOG_NAME).error(msg)
            raise ValueError(msg)
        self.element_id = element_id
        # To avoid having those elements hidden in production configuration, write a line every time the class is instantiated.
        msg = "DebugModelElement %s added" % element_id
        logging.getLogger(DEBUG_LOG_NAME).info(msg)
        print(msg, file=sys.stderr)

    def get_id(self):
        """Get the element ID."""
        return self.element_id

    def get_child_elements(self):  # skipcq: PYL-R0201
        """
        Get all possible child model elements of this element.
        @return empty list as there are no children of this element.
        """
        return None

    def get_match_element(self, path, match_context):
        """@return Always return a match."""
        msg = 'DebugModelElement path = "%s/%s", unmatched = "%s"' % (path, self.element_id, repr(match_context.match_data))
        logging.getLogger(DEBUG_LOG_NAME).info(msg)
        print(msg, file=sys.stderr)
        return MatchElement('%s/%s' % (path, self.element_id), b"", b"", None)
