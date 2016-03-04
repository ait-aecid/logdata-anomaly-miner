from collections import deque

class ParserMatch:
  """Objects of this class store information about a complete
  model match. Unlike the MatchElement, this class also provides
  fields to store information commonly used when dealing with
  the match."""

  def __init__(self, matchElement):
    """Initialize the match."""
    self.matchElement=matchElement
    self.matchDictionary=None
    self.defaultTimestamp=None


  def getMatchElement(self):
    return(self.matchElement)


  def getMatchDictionary(self):
    if self.matchDictionary!=None: return(self.matchDictionary)
    stack=deque()
    stack.append([self.matchElement])
    dict={}
    while(len(stack)):
      matchList=stack.pop()
      for testMatch in matchList:
        dict[testMatch.path]=testMatch
        children=testMatch.children
        if (children!=None) and (len(children)!=0): stack.append(children)
    self.matchDictionary=dict
    return(dict)


  def setDefaultTimestamp(self, timestamp):
    self.defaultTimestamp=timestamp


  def getDefaultTimestamp(self):
    """Get the default timestamp value for this MatchElement.
    @return the timestamp as number of seconds since 1970."""
    return(self.defaultTimestamp)

  def __str__(self):
    return('ParserMatch (%s): %s' % (self.defaultTimestamp, self.matchElement.annotateMatch('  ')))
