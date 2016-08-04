# This file collects various classes useful to filter parsed atoms
# and pass them to different handlers.

from aminer.parsing import ParsedAtomHandlerInterface


class SubhandlerFilter(ParsedAtomHandlerInterface):
  """Handlers of this class pass the received atoms to one or
  more subhandlers. Depending on configuration, the atom is passed
  to all subhandlers or only up to the first suitable to handle
  the atom."""
  def __init__(self, subhandlerList, stopWhenHandledFlag=False):
    if (not(isinstance(subhandlerList, list))) or (not(all(isinstance(handler, ParsedAtomHandlerInterface) for handler in subhandlerList))):
      raise Exception('Only subclasses of ParsedAtomHandlerInterface allowed in subhandlerList')
    self.subhandlerList=subhandlerList
    self.stopWhenHandledFlag=stopWhenHandledFlag

  def receiveParsedAtom(self, atomData, match):
    """Pass the atom to the subhandlers.
    @return false when no subhandler was able to handle the atom."""
    result=False
    for handler in self.subhandlerList:
      handlerResult=handler.receiveParsedAtom(atomData, match)
      if handlerResult==True:
        result=True
        if self.stopWhenHandledFlag:
          break
    return(result)


class MatchPathFilter(ParsedAtomHandlerInterface):
  """This class just splits incoming matches according to existance
  of pathes in the match."""

  def __init__(self, parsedAtomHandlerLookupList, defaultParsedAtomHandler):
    """Initialize the filter.
    @param parsedAtomHandlerLookupList has to contain tuples with
    search path string and handler. When the handler is None,
    the filter will just drop a received atom without forwarding."""
    self.parsedAtomHandlerLookupList=parsedAtomHandlerLookupList
    self.defaultParsedAtomHandler=defaultParsedAtomHandler


  def receiveParsedAtom(self, atomData, match):
    matchDict=match.getMatchDictionary()
    for pathName, targetHandler in self.parsedAtomHandlerLookupList:
      if matchDict.has_key(pathName):
        if targetHandler!=None:
          targetHandler.receiveParsedAtom(atomData, match)
        return True
    return(self.defaultParsedAtomHandler.receiveParsedAtom(atomData, match))


class MatchValueFilter(ParsedAtomHandlerInterface):
  """This class just splits incoming matches using a given match
  value and forward them to different handlers."""

  def __init__(self, targetPath, parsedAtomHandlerDict, defaultParsedAtomHandler):
    """Initialize the splitter."""
    self.targetPath=targetPath
    self.parsedAtomHandlerDict=parsedAtomHandlerDict
    self.defaultParsedAtomHandler=defaultParsedAtomHandler


  def receiveParsedAtom(self, atomData, match):
    targetValue=match.getMatchDictionary().get(self.targetPath, None)
    if targetValue!=None: targetValue=targetValue.matchObject
    targetHandler=self.parsedAtomHandlerDict.get(targetValue,
        self.defaultParsedAtomHandler)
    return(targetHandler.receiveParsedAtom(atomData, match))
