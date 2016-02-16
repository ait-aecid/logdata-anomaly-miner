class MatchValueQueueSplitter:
  """This class just splits incoming matches using a given match
  value and forward them to different queues."""

  def __init__(self, targetPath, parsedAtomHandlerDict, defaultParsedAtomHandler):
    """Initialize the splitter."""
    self.targetPath=targetPath
    self.parsedAtomHandlerDict=parsedAtomHandlerDict
    self.defaultParsedAtomHandler=defaultParsedAtomHandler


  def receiveParsedAtom(self, atomData, match):
    targetValue=match.getMatchDictionary().get(self.targetPath, None)
    targetHandler=self.parsedAtomHandlerDict.get(targetValue, self.defaultParsedAtomHandler)
    targetHandler.receiveParsedAtom(atomData, match)


  def checkTriggers(self):
    return(1<<16)
