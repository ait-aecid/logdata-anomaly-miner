class FirstMatchModelElement:
  """This class defines a model element to return the match from
  the the first matching child model within a given list."""
  def __init__(self, id, children):
    self.id=id
    self.children=children
    if (children == None) or (None in children): raise Exception('Invalid children list')

  def getChildElements(self):
    return(children)

  def getMatchElement(self, path, matchContext):
    """@return None when there is no match, MatchElement otherwise."""
    currentPath="%s/%s" % (path, self.id)

    matchData=matchContext.matchData
    for childElement in self.children:
      childMatch=childElement.getMatchElement(currentPath, matchContext)
      if childMatch != None: return(childMatch)
      matchContext.matchData=matchData
    return(None)
