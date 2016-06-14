import MatchElement

class RepeatedElementDataModelElement:
  """Objects of this class match on repeats of a given element."""
  def __init__(self, id, repeatedElement, minRepeat=-1, maxRepeat=-1, repeatRef=None):
    self.id=id
    self.repeatedElement=repeatedElement

  def getChildElements(self):
    return([repeatedElement])

  def getMatchElement(self, path, matchContext):
    """Find a suitable number of repeats."""
    currentPath="%s/%s" % (path, self.id)
    currentPos=0

    minRepeat=0
    maxRepeat=0x100000

    startData=matchContext.matchData
    matches=[]
    matchCount=0
    while matchCount != maxRepeat:
      childMatch=self.repeatedElement.getMatchElement(
          '%s/%s' % (currentPath, matchCount),
          matchContext)
      if childMatch == None: break
      matches+=[childMatch]
      matchCount+=1
    if matchCount < minRepeat:
      matchContext.matchData=startData
      return(None)

    return(MatchElement.MatchElement(currentPath,
        startData[:len(startData)-len(matchContext.matchData)],
        None, matches))
