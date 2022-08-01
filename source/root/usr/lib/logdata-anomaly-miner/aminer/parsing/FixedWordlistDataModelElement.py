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

from aminer.parsing.ModelElementInterface import ModelElementInterface
from aminer.parsing.MatchElement import MatchElement


class FixedWordlistDataModelElement(ModelElementInterface):
    """
    This class defines a model element to detect fixed strings from a list of words.
    The match will return the position of the word in the search list, thus the sorting of the list is important. Apart from that, the
    wordlist must not contain any words, that are identical to the beginning of words later in the list. In that case, the longer match
    could never be detected.
    """

    def __init__(self, element_id: str, wordlist: list):
        """
        Create the model element.
        @param wordlist the list of words to search for. If it does not fulfill the sorting criteria mentioned in the class documentation,
               an Exception will be raised.
        """
        super().__init__(element_id, wordlist=wordlist)

    def get_match_element(self, path: str, match_context):
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
