from collections import deque

class ParserMatch:
  """Objects of this class store information about a complete
  model match. Unlike the MatchElement, this class also provides
  fields to store information commonly used when dealing with
  the match."""

  def __init__(self, matchElement, parsingProcessData=None):
    """Initialize the match.
    @param parsingProcessData this parameter might provide more
    information about the parsing process, e.g. when parsing produced
    warnings. The data is specific for the source producing the
    match."""
    self.matchElement=matchElement
    self.parsingProcessData=parsingProcessData
    self.matchDictionary=None


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


  def __str__(self):
    return('ParserMatch: %s' % (self.matchElement.annotateMatch('  ')))
