import MatchElement

class VariableByteDataModelElement:
  def __init__(self, id, alphabet):
    self.id=id
    self.alphabet=alphabet

  def getChildElements(self):
    return(None)

  def getMatchElement(self, path, matchContext):
    """Find the maximum number of bytes matching the given alphabet.
    @return a match when at least one byte was found within alphabet."""
    data=matchContext.matchData
    matchLen=0
    for testByte in data:
      if not(testByte in self.alphabet): break
      matchLen+=1

    if matchLen == 0: return(None)
    matchData=data[:matchLen]
    matchContext.update(matchData)
    return(MatchElement.MatchElement("%s/%s" % (path, self.id),
        matchData, matchData, None))
