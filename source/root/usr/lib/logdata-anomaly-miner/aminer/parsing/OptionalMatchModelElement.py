import MatchElement

class OptionalMatchModelElement:
  """This class defines a model element tries to match against
  a given model element and if that fails returns a zero length
  match anyway."""
  def __init__(self, id, optionalElement):
    self.id=id
    self.optionalElement=optionalElement

  def getChildElements(self):
    return([optionalElement])

  def getMatchElement(self, path, matchContext):
    """@return the embedded child match or an empty match."""
    currentPath="%s/%s" % (path, self.id)

    startData=matchContext.matchData
    match=self.optionalElement.getMatchElement(currentPath, matchContext)
    if match == None:
      return(MatchElement.MatchElement("%s/%s" % (path, self.id),
          '', None, None))

    return(MatchElement.MatchElement(currentPath,
        startData[:len(startData)-len(matchContext.matchData)],
        None, [match]))
