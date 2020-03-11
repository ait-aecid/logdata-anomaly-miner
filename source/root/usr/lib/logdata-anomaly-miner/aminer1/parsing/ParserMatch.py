"""This module defines a matching parser model element."""

from collections import deque

class ParserMatch:
  """Objects of this class store information about a complete
  model match. Unlike the MatchElement, this class also provides
  fields to store information commonly used when dealing with
  the match."""

  def __init__(self, matchElement, parsingProcessData=None):
    """Initialize the match.
    @param matchElement the root MatchElement from the parsing
    process.
    @param parsingProcessData this parameter might provide more
    information about the parsing process, e.g. when parsing produced
    warnings. The data is specific for the source producing the
    match."""
    self.matchElement = matchElement
    self.parsingProcessData = parsingProcessData
    self.matchDictionary = None

  def getMatchElement(self):
    """Return the matching element."""
    return self.matchElement

  def getMatchDictionary(self):
    """Return a dictionary of all children matches."""
    if self.matchDictionary is not None:
      return self.matchDictionary
    stack = deque()
    stack.append([self.matchElement])
    resultDict = {}
    while stack:
      matchList = stack.pop()
      for testMatch in matchList:
        resultDict[testMatch.path] = testMatch
        children = testMatch.children
        if (children is not None) and children:
          stack.append(children)
    self.matchDictionary = resultDict
    return resultDict


  def __str__(self):
    return 'ParserMatch: %s' % (self.matchElement.annotateMatch('  '))
