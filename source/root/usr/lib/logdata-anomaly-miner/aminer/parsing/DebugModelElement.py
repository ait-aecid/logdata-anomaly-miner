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
    Thus, it can never fail to match and can be inserted at any position in the parsing tree, where matching itself does not alter parsing
    flow (see e.g. FirstMatchModelElement). It will immediately write the current state of the match to stderr for inspection.
    """

    def __init__(self, element_id: str):
        """
        Initialize the ModelElement.
        @param element_id an identifier for the ModelElement which is shown in the path.
        """
        super().__init__(element_id)
        # To avoid having those elements hidden in production configuration, write a line every time the class is instantiated.
        msg = "DebugModelElement %s added" % element_id
        logging.getLogger(DEBUG_LOG_NAME).info(msg)
        print(msg, file=sys.stderr)

    def get_match_element(self, path: str, match_context):
        """
        @param path to be printed in the MatchElement.
        @param match_context the match_context to be analyzed.
        @return Always return a match.
        """
        msg = 'DebugModelElement path = "%s/%s", unmatched = "%s"' % (path, self.element_id, repr(match_context.match_data))
        logging.getLogger(DEBUG_LOG_NAME).info(msg)
        print(msg, file=sys.stderr)
        return MatchElement('%s/%s' % (path, self.element_id), b"", b"", None)
