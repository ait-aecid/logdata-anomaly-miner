from aminer.parsing import MatchContext
from aminer.parsing import ParserMatch

class SimpleParsingModelRawAtomHandler:

  def __init__(self, parsingModel, parsedAtomHandlers, unparsedAtomHandlers,
      defaultTimestampPath=None):
    self.parsingModel=parsingModel
    self.parsedAtomHandlers=parsedAtomHandlers
    self.unparsedAtomHandlers=unparsedAtomHandlers
    self.defaultTimestampPath=defaultTimestampPath

  def receiveAtom(self, atomData):
    matchContext=MatchContext.MatchContext(atomData)
    matchElement=self.parsingModel.getMatchElement('', matchContext)
    if matchElement!=None:
      parserMatch=ParserMatch.ParserMatch(matchElement)
      if self.defaultTimestampPath!=None:
        tsMatch=parserMatch.getMatchDictionary().get(self.defaultTimestampPath, None)
        if tsMatch!=None:
          parserMatch.setDefaultTimestamp(tsMatch.matchObject[1])
      for handler in self.parsedAtomHandlers:
        handler.receiveParsedAtom(atomData, parserMatch)
    else:
      for handler in self.unparsedAtomHandlers:
        handler.receiveUnparsedAtom(atomData, matchContext.matchData, None)
