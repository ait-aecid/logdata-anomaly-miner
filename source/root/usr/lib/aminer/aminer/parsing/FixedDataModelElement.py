import MatchElement

class FixedDataModelElement:
  def __init__(self, id, fixedData):
    self.id=id
    self.fixedData=fixedData

  def getChildElements(self):
    return(None)

  def getMatchElement(self, path, matchContext):
    """@return None when there is no match, MatchElement otherwise."""
    if not(matchContext.matchData.startswith(self.fixedData)): return(None)
    matchContext.update(self.fixedData)
    return(MatchElement.MatchElement("%s/%s" % (path, self.id),
        self.fixedData, self.fixedData, None))
