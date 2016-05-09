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


  def annotateMatch(self, indentStr):
    """Annotate a given match element showing the match path elements
    and the parsed values.
    @param indentStr if None, all elements are separated just
    with a single space, no matter how deep the nesting level
    of those elements is. If not None, all elements are put into
    an own lines, that is prefixed by the given indentStr and
    indenting is increased by two spaces for earch level."""
    nextIndent=None
    result=None
    if indentStr==None:
      result='%s: %s (\'%s\')' % (self.path, self.matchObject, self.matchString)
    else:
      result='%s%s: %s (\'%s\')' % (indentStr, self.path, self.matchObject, self.matchString)
      nextIndent=indentStr+'  '
    if self.children != None:
      for childMatch in self.children:
        if nextIndent==None:
          result+=' '+childMatch.annotateMatch(None)
        else:
          result+='\n'+childMatch.annotateMatch(nextIndent)
    return(result)
