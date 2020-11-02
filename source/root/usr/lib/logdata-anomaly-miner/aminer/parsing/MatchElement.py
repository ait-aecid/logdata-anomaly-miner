"""
This module provides only the MatchElement class to store results from parser element matching process.

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
from aminer import AMinerConfig


class MatchElement:
    """This class allows storage and handling of data related to a match found by a model element."""

    def __init__(self, path, match_string, match_object, children):
        """
        Initialize the MatchElement.
        @param path when None, this element is anonymous. Hence it cannot be added to the result data and cannot have children.
        @param match_string the part of the input bytes string covered by the given match.
        @param match_object the matchString converted to an object for matchers detecting more complex data types, e.g., integer
        numbers or IP addresses.
        """
        if (not path) and children:
            msg = "Anonymous match may not have children"
            logging.getLogger(AMinerConfig.DEBUG_LOG_NAME).error(msg)
            raise Exception(msg)
        self.path = path
        self.match_string = match_string
        self.match_object = match_object
        self.children = children

    def get_path(self):
        """
        Get the path of this element.
        @return the path string.
        """
        return self.path

    def get_match_string(self):
        """Get the log_atom string part this match element is matching."""
        return self.match_string

    def get_match_object(self):
        """Get the matched data converted to an object of suitable type."""
        return self.match_object

    def get_children(self):
        """
        Get the submatch children of this match, if any.
        @return a list of submatches or None
        """
        return self.children

    def annotate_match(self, indent_str):
        """
        Annotate a given match element showing the match path elements and the parsed values.
        @param indent_str if None, all elements are separated just with a single space, no matter how deep the nesting level
        of those elements is. If not None, all elements are put into an own lines, that is prefixed by the given indent_str and
        indenting is increased by two spaces for each level.
        """
        next_indent = None
        result = None
        if indent_str is None:
            result = '%s: %s' % (self.path, repr(self.match_object))
        else:
            result = '%s%s: %s' % (indent_str, self.path, repr(self.match_object))
            next_indent = indent_str + '  '
        if self.children is not None:
            for child_match in self.children:
                if next_indent is None:
                    result += ' ' + child_match.annotate_match(None)
                else:
                    result += '\n' + child_match.annotate_match(next_indent)
        return result

    def serialize_object(self):
        """
        Create a serialization of this match element and all the children.
        With sane and unique path elements, the serialized object will also be unique.
        """
        chld = []
        if self.children:
            for child_match in self.children:
                chld.append(child_match.serialize_object())
        return {"path": self.path, "matchobject": self.match_object, "matchString": self.match_string, "children": chld}

    def __str__(self):
        """Get a string representation of this match element excluding the children."""
        num_children = 0
        if self.children is not None:
            num_children = len(self.children)
        return 'MatchElement: path = %s, string = %s, object = %s, children = %d' % (
            self.path, repr(self.match_string), repr(self.match_object), num_children)
