import MatchElement

class DecimalIntegerValueModelElement:
  """This class defines a model to parse integer values with optional
  signum or padding. If both are present, it is signum has to be
  before the padding characters."""

  SIGN_TYPE_NONE='none'
  SIGN_TYPE_OPTIONAL='optional'
  SIGN_TYPE_MANDATORY='mandatory'

  PAD_TYPE_NONE='none'
  PAD_TYPE_ZERO='zero'
  PAD_TYPE_BLANK='blank'

  def __init__(self, id, valueSignType=SIGN_TYPE_NONE, valuePadType=PAD_TYPE_NONE):
    self.id=id
    self.startCharacters=None
    if valueSignType==DecimalIntegerValueModelElement.SIGN_TYPE_NONE: self.startCharacters='0123456789'
    elif valueSignType==DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL: self.startCharacters='-0123456789'
    elif valueSignType==DecimalIntegerValueModelElement.SIGN_TYPE_MANDATORY: self.startCharacters='+-'
    else: raise Error('Invalid valueSignType "%s"' % valueSignType)

    self.padCharacters=''
    if valuePadType==DecimalIntegerValueModelElement.PAD_TYPE_NONE: pass
    elif valuePadType==DecimalIntegerValueModelElement.PAD_TYPE_ZERO:
      self.padCharacters='0'
    elif valuePadType==DecimalIntegerValueModelElement.PAD_TYPE_BLANK:
      self.padCharacters=' '
    else: raise Error('Invalid valuePadType "%s"' % valueSignType)
    self.valuePadType=valuePadType

  def getChildElements(self):
    return(None)

  def getMatchElement(self, path, matchContext):
    """Find the maximum number of bytes forming a integer number
    according to the parameters specified
    @return a match when at least one byte being a digit was found"""
    data=matchContext.matchData

    allowedCharacters=self.startCharacters
    if (len(data)==0) or (not(data[0] in allowedCharacters)): return(None)
    matchLen=1

    allowedCharacters=self.padCharacters
    for testByte in data[matchLen:]:
      if not(testByte in allowedCharacters): break
      matchLen+=1
    numStartPos=matchLen
    allowedCharacters='0123456789'
    for testByte in data[matchLen:]:
      if not(testByte in allowedCharacters): break
      matchLen+=1

    if matchLen == 1:
      if data[0] not in '0123456789':
        return(None)
    elif numStartPos == matchLen:
      return(None)

    matchString=data[:matchLen]
    matchValue=int(matchString)
    matchContext.update(matchString)
    return(MatchElement.MatchElement("%s/%s" % (path, self.id),
        matchString, matchValue, None))
