import MatchElement

class WhiteSpaceLimitedDataModelElement:
  def __init__(self, id):
    self.id=id

  def getChildElements(self):
    return(None)

  """Find the maximum number of bytes before encountering whitespace
or end of data.
@return a match when at least one byte was found."""
  def getMatchElement(self, path, matchContext):
    data=matchContext.matchData
    matchLen=0
    for testByte in data:
      if testByte in ' \t': break
      matchLen+=1

    if matchLen == 0: return(None)
    matchData=data[:matchLen]
    matchContext.update(matchData)
    return(MatchElement.MatchElement("%s/%s" % (path, self.id),
        matchData, matchData, None))
