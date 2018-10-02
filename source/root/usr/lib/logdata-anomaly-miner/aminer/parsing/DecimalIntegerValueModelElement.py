"""This module defines an model element for integer number parsing."""

from aminer.parsing import ModelElementInterface
from aminer.parsing.MatchElement import MatchElement

class DecimalIntegerValueModelElement(ModelElementInterface):
  """This class defines a model to parse integer values with optional
  signum or padding. If both are present, it is signum has to be
  before the padding characters."""

  SIGN_TYPE_NONE = 'none'
  SIGN_TYPE_OPTIONAL = 'optional'
  SIGN_TYPE_MANDATORY = 'mandatory'

  PAD_TYPE_NONE = 'none'
  PAD_TYPE_ZERO = 'zero'
  PAD_TYPE_BLANK = 'blank'

  def __init__(
      self, pathId, valueSignType=SIGN_TYPE_NONE, valuePadType=PAD_TYPE_NONE):
    self.pathId = pathId
    self.startCharacters = None
    if valueSignType == DecimalIntegerValueModelElement.SIGN_TYPE_NONE:
      self.startCharacters = b'0123456789'
    elif valueSignType == DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL:
      self.startCharacters = b'-0123456789'
    elif valueSignType == DecimalIntegerValueModelElement.SIGN_TYPE_MANDATORY:
      self.startCharacters = b'+-'
    else:
      raise Exception('Invalid valueSignType "%s"' % valueSignType)

    self.padCharacters = b''
    if valuePadType == DecimalIntegerValueModelElement.PAD_TYPE_NONE:
      pass
    elif valuePadType == DecimalIntegerValueModelElement.PAD_TYPE_ZERO:
      self.padCharacters = b'0'
    elif valuePadType == DecimalIntegerValueModelElement.PAD_TYPE_BLANK:
      self.padCharacters = b' '
    else:
      raise Exception('Invalid valuePadType "%s"' % valueSignType)
    self.valuePadType = valuePadType

  def getChildElements(self):
    """Get all possible child model elements of this element.
    @return empty list as there are no children of this element."""
    return []

  def getMatchElement(self, path, matchContext):
    """Find the maximum number of bytes forming a integer number
    according to the parameters specified.
    @return a match when at least one byte being a digit was found"""
    data = matchContext.matchData

    allowedCharacters = self.startCharacters
    if not data or (data[0] not in allowedCharacters):
      return None
    matchLen = 1

    allowedCharacters = self.padCharacters
    for testByte in data[matchLen:]:
      if testByte not in allowedCharacters:
        break
      matchLen += 1
    numStartPos = matchLen
    allowedCharacters = b'0123456789'
    for testByte in data[matchLen:]:
      if testByte not in allowedCharacters:
        break
      matchLen += 1

    if matchLen == 1:
      if data[0] not in b'0123456789':
        return None
    elif numStartPos == matchLen:
      return None

    matchString = data[:matchLen]
    matchValue = int(matchString)
    matchContext.update(matchString)
    return MatchElement(
        '%s/%s' % (path, self.pathId), matchString, matchValue, None)
