import MatchElement

class DelimitedDataModelElement:
  """Find a string delimited by given delimiter string, possibly
  a match of zero byte length"""
  def __init__(self, id, delimiter):
    self.id=id
    self.delimiter=delimiter

  def getChildElements(self):
    return(None)

  def getMatchElement(self, path, matchContext):
    """Find the maximum number of bytes before encountering the
    delimiter.
    @return a match when at least one byte was found but not the
    delimiter itself."""
    data=matchContext.matchData
    matchLen=data.find(self.delimiter)
    if (matchLen < 0): return(None)
    matchData=data[:matchLen]
    matchContext.update(matchData)
    return(MatchElement.MatchElement("%s/%s" % (path, self.id),
        matchData, matchData, None))
