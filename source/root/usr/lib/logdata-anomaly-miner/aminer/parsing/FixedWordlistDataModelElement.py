"""
This module defines a model element to detect fixed strings from a list of words.

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
from aminer.parsing.ModelElementInterface import ModelElementInterface
from aminer.parsing.MatchElement import MatchElement


class FixedWordlistDataModelElement(ModelElementInterface):
    """
    This class defines a model element to detect fixed strings from a list of words.
    The match will return the position of the word in the search list, thus the sorting of the list is important. Apart from that, the
    wordlist must not contain any words, that are identical to the beginning of words later in the list. In that case, the longer match
    could never be detected.
    """

    def __init__(self, element_id, wordlist):
        """
        Create the model element.
        @param wordlist the list of words to search for. If it does not fulfill the sorting criteria mentioned in the class documentation,
        an Exception will be raised.
        """
        if not isinstance(element_id, str):
            msg = "element_id has to be of the type string."
            logging.getLogger(DEBUG_LOG_NAME).error(msg)
            raise TypeError(msg)
        if len(element_id) < 1:
            msg = "element_id must not be empty."
            logging.getLogger(DEBUG_LOG_NAME).error(msg)
            raise ValueError(msg)
        self.element_id = element_id

        if not isinstance(wordlist, list):
            msg = "wordlist has to be of the type list."
            logging.getLogger(DEBUG_LOG_NAME).error(msg)
            raise TypeError(msg)
        if len(wordlist) < 2:
            msg = "wordlist must have two or more elements."
            logging.getLogger(DEBUG_LOG_NAME).error(msg)
            raise ValueError(msg)
        for word in wordlist:
            if not isinstance(word, bytes):
                msg = "words from the wordlist must be of the type bytes."
                logging.getLogger(DEBUG_LOG_NAME).error(msg)
                raise TypeError(msg)

        for test_pos, ref_word in enumerate(wordlist):
            for test_word in wordlist[test_pos + 1:]:
                if test_word.startswith(ref_word):
                    msg = "Word %s would be shadowed by word %s at lower position" % (repr(test_word), repr(ref_word))
                    logging.getLogger(DEBUG_LOG_NAME).error(msg)
                    raise ValueError(msg)
        self.wordlist = wordlist

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
        """@return None when there is no match, MatchElement otherwise."""
        data = match_context.match_data
        match_data = None
        word_pos = 0
        for word in self.wordlist:
            if data.startswith(word):
                match_data = word
                break
            word_pos += 1

        if match_data is None:
            return None

        match_context.update(match_data)
        return MatchElement("%s/%s" % (path, self.element_id), match_data, word_pos, None)
