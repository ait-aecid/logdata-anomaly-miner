import MatchElement

class FixedWordlistDataModelElement:
  def __init__(self, id, wordlist):
    self.id=id
    self.wordlist=wordlist

  def getChildElements(self):
    return(None)

  def getMatchElement(self, path, matchContext):
    """@return None when there is no match, MatchElement otherwise."""
    data=matchContext.matchData
    matchData=None
    wordPos=0
    for word in self.wordlist:
      if data.startswith(word):
        matchData=word
        break
      wordPos+=1

    if matchData == None: return(None)

    matchContext.update(matchData)
    return(MatchElement.MatchElement("%s/%s" % (path, self.id),
        matchData, wordPos, None))
