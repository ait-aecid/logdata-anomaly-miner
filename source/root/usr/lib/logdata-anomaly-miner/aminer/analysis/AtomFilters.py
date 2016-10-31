# This file collects various classes useful to filter log atoms
# and pass them to different handlers.

from aminer.input import AtomHandlerInterface


class SubhandlerFilter(AtomHandlerInterface):
  """Handlers of this class pass the received atoms to one or
  more subhandlers. Depending on configuration, the atom is passed
  to all subhandlers or only up to the first suitable to handle
  the atom."""
  def __init__(self, subhandlerList, stopWhenHandledFlag=False):
    """@param subhandlerList when not None, initialize this filter
    with the given list of handlers."""
    if subhandlerList==None:
      self.subhandlerList=[]
    else:
      if (not(isinstance(subhandlerList, list))) or (not(all(isinstance(handler, AtomHandlerInterface) for handler in subhandlerList))):
        raise Exception('Only subclasses of AtomHandlerInterface allowed in subhandlerList')
      self.subhandlerList=[None]*len(subhandlerList)
      for handlerPos in range(0, len(subhandlerList)):
        self.subhandlerList[handlerPos]=(subhandlerList[handlerPos], stopWhenHandledFlag)

  def addHandler(self, atomHandler, stopWhenHandledFlag=False):
    self.subhandlerList.append((atomHandler, stopWhenHandledFlag))

  def receiveAtom(self, logAtom):
    """Pass the atom to the subhandlers.
    @return false when no subhandler was able to handle the atom."""
    result=False
    for handler, stopWhenHandledFlag in self.subhandlerList:
      handlerResult=handler.receiveAtom(logAtom)
      if handlerResult==True:
        result=True
        if stopWhenHandledFlag:
          break
    return(result)


class MatchPathFilter(AtomHandlerInterface):
  """This class just splits incoming matches according to existance
  of pathes in the match."""

  def __init__(self, parsedAtomHandlerLookupList, defaultParsedAtomHandler):
    """Initialize the filter.
    @param parsedAtomHandlerLookupList has to contain tuples with
    search path string and handler. When the handler is None,
    the filter will just drop a received atom without forwarding.
    @param defaultParsedAtomHandler invoke this handler when no
    handler was found for given match path or do not invoke any
    handler when None."""
    self.parsedAtomHandlerLookupList=parsedAtomHandlerLookupList
    self.defaultParsedAtomHandler=defaultParsedAtomHandler


  def receiveAtom(self, logAtom):
    """Receive an atom and pass it to the subhandlers.
    @return False when logAtom did not contain match data or was
    not forwarded to any handler, True otherwise."""
    if logAtom.parserMatch==None:
      return(False)
    matchDict=logAtom.parserMatch.getMatchDictionary()
    for pathName, targetHandler in self.parsedAtomHandlerLookupList:
      if matchDict.has_key(pathName):
        if targetHandler!=None:
          targetHandler.receiveAtom(logAtom)
        return True
    if self.defaultParsedAtomHandler==None: return(False)
    self.defaultParsedAtomHandler.receiveAtom(logAtom)
    return(True)


class MatchValueFilter(AtomHandlerInterface):
  """This class just splits incoming matches using a given match
  value and forward them to different handlers."""

  def __init__(self, targetPath, parsedAtomHandlerDict, defaultParsedAtomHandler):
    """Initialize the splitter.
    @param defaultParsedAtomHandler invoke this default handler
    when no value handler was found or do not invoke any handler
    when None."""
    self.targetPath=targetPath
    self.parsedAtomHandlerDict=parsedAtomHandlerDict
    self.defaultParsedAtomHandler=defaultParsedAtomHandler


  def receiveAtom(self, logAtom):
    if logAtom.parserMatch==None:
      return(False)
    targetValue=logAtom.parserMatch.getMatchDictionary().get(self.targetPath, None)
    if targetValue!=None: targetValue=targetValue.matchObject
    targetHandler=self.parsedAtomHandlerDict.get(targetValue,
        self.defaultParsedAtomHandler)
    if targetHandler==None: return(False)
    targetHandler.receiveAtom(logAtom)
    return(True)
