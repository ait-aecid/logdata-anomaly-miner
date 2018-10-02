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

  def __init__(self, pathId, wordlist):
    """Create the model element.
    @param wordlist the list of words to search for. If it does
    not fulfill the sorting criteria mentioned in the class documentation,
    an Exception will be raised."""
    self.pathId = pathId
    self.wordlist = wordlist
    for testPos, refWord in enumerate(wordlist):
      for testWord in wordlist[testPos+1:]:
        if testWord.startswith(refWord):
          raise Exception(
              'Word %s would be shadowed by word %s at lower position' % (
                  repr(testWord), repr(refWord)))


  def getChildElements(self):
    """Get all possible child model elements of this element.
    @return None as there are no children of this element."""
    return None

  def getMatchElement(self, path, matchContext):
    """@return None when there is no match, MatchElement otherwise."""
    data = matchContext.matchData
    matchData = None
    wordPos = 0
    for word in self.wordlist:
      if data.startswith(word):
        matchData = word
        break
      wordPos += 1

    if matchData is None:
      return None

    matchContext.update(matchData)
    return MatchElement(
        "%s/%s" % (path, self.pathId), matchData, wordPos, None)
