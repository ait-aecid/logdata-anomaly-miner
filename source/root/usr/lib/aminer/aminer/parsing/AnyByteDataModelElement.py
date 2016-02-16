import MatchElement

class AnyByteDataModelElement:
  """This class matches any byte but at least one. Thus a match
  will always span the complete data from beginning to end."""
  def __init__(self, id):
    self.id=id

  def getChildElements(self):
    return(None)

  def getMatchElement(self, path, matchContext):
    """Just return a match including all data from the context"""
    matchData=matchContext.matchData
    if len(matchData) == 0: return(None)
    matchContext.update(matchData)
    return(MatchElement.MatchElement("%s/%s" % (path, self.id),
        matchData, matchData, None))
