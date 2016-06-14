import MatchElement

class SequenceModelElement:
  """This class defines an element to find matches that comprise
  matches of all given child model elements."""
  def __init__(self, id, children):
    self.id=id
    self.children=children

  def getChildElements(self):
    return(children)

  """@return None when there is no match, MatchElement otherwise."""
  def getMatchElement(self, path, matchContext):
    currentPath="%s/%s" % (path, self.id)
    currentPos=0

    startData=matchContext.matchData
    matches=[]
    for childElement in self.children:
      childMatch=childElement.getMatchElement(currentPath,
          matchContext)
      if(childMatch==None):
        matchContext.matchData=startData
        return(None);
      matches+=[childMatch]

    return(MatchElement.MatchElement(currentPath,
        startData[:len(startData)-len(matchContext.matchData)],
        None, matches))
