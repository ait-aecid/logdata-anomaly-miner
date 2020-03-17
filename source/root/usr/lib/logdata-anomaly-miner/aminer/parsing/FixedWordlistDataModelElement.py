"""This module defines a model element to detect fixed strings
from a list of words."""

from aminer.parsing import ModelElementInterface
from aminer.parsing.MatchElement import MatchElement

class FixedWordlistDataModelElement(ModelElementInterface):
  """This class defines a model element to detect fixed strings
  from a list of words. The match will return the position of
  the word in the search list, thus the sorting of the list is
  important. Apart from that, the wordlist must not contain any
  words, that are identical to the beginning of words later in
  the list. In that case, the longer match could never be detected."""

  def __init__(self, path_id, wordlist):
    """Create the model element.
    @param wordlist the list of words to search for. If it does
    not fulfill the sorting criteria mentioned in the class documentation,
    an Exception will be raised."""
    self.path_id = path_id
    self.wordlist = wordlist
    for test_pos, ref_word in enumerate(wordlist):
      for test_word in wordlist[test_pos+1:]:
        if test_word.startswith(ref_word):
          raise Exception(
              'Word %s would be shadowed by word %s at lower position' % (
                  repr(test_word), repr(ref_word)))


  def get_child_elements(self):
    """Get all possible child model elements of this element.
    @return None as there are no children of this element."""
    return None

  def get_match_element(self, path, match_context):
    """@return None when there is no match, MatchElement otherwise."""
    data = match_context.matchData
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
    return MatchElement(
        "%s/%s" % (path, self.path_id), match_data, word_pos, None)
