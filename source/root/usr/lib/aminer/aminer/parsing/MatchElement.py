class MatchElement:
  """This class allows storage and handling of data related to
  a match found by a model element."""

  def __init__(self, path, matchString, matchObject, children):
    """Initialize the MatchElement.
    @param path when None, this element is anonymous. Hence it
    cannot be added to the result data and cannot have children.
    @param matchString the part of the input string covered by
    the given match."""
    if (path==None) and (len(children)!=0):
      raise Error("Anonymous match may not have children")
    self.path=path
    self.matchString=matchString
    self.matchObject=matchObject
    self.children=children


  def getPath(self):
    return(self.path)


  def getMatchString(self):
    return(self.matchString)


  def getMatchObject(self):
    return(self.matchObject)


  def getChildren(self):
    return(self.children)


  def annotateMatch(self, intendStr):
    result='%s%s: %s (\'%s\')' % (intendStr, self.path, self.matchObject, self.matchString)
    if len(intendStr) == 0: intendStr=b'\n  '
    else: intendStr+='  '

    if self.children != None:
      for childMatch in self.children:
        result+=childMatch.annotateMatch(intendStr)
    return(result)
