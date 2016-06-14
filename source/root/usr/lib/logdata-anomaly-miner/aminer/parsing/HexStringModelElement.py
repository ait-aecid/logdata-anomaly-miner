import MatchElement

class HexStringModelElement:
  """This class just tries to strip off as many hex bytes as possible
  from a given data string."""
  def __init__(self, id, upperCase=False):
    self.id=id
    if upperCase:
      self.charStart=ord('A')
    else:
      self.charStart=ord('a')

  def getChildElements(self):
    return(None)

  def getMatchElement(self, path, matchContext):
    """Find the maximum number of bytes forming a integer number
    according to the parameters specified
    @return a match when at least one byte being a digit was found"""
    data=matchContext.matchData
    matchLen=0
    for testByte in data:
      bVal=ord(testByte)
      if ((bVal<0x30) or (bVal>0x39)) and ((bVal<self.charStart) or (bVal-self.charStart>5)):
        break
      matchLen+=1

    if (matchLen==0): return(None)

    matchString=data[:matchLen]
    matchContext.update(matchString)
    return(MatchElement.MatchElement("%s/%s" % (path, self.id),
        matchString, matchString, None))
