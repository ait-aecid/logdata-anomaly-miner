"""This module defines an model element for decimal number parsing
as float."""

from aminer.parsing import ModelElementInterface
from aminer.parsing.MatchElement import MatchElement

class DecimalFloatValueModelElement(ModelElementInterface):
  """This class defines a model to parse decimal values with optional
  signum, padding or exponent. With padding, the signum has to
  be found before the padding characters."""

  SIGN_TYPE_NONE = 'none'
  SIGN_TYPE_OPTIONAL = 'optional'
  SIGN_TYPE_MANDATORY = 'mandatory'

  PAD_TYPE_NONE = 'none'
  PAD_TYPE_ZERO = 'zero'
  PAD_TYPE_BLANK = 'blank'

  EXP_TYPE_NONE = 'none'
  EXP_TYPE_OPTIONAL = 'optional'
  EXP_TYPE_MANDATORY = 'mandatory'

  def __init__(
      self, pathId, valueSignType=SIGN_TYPE_NONE, valuePadType=PAD_TYPE_NONE,
      exponentType=EXP_TYPE_NONE):
    self.pathId = pathId
    self.startCharacters = None
    if valueSignType == DecimalFloatValueModelElement.SIGN_TYPE_NONE:
      self.startCharacters = b'0123456789'
    elif valueSignType == DecimalFloatValueModelElement.SIGN_TYPE_OPTIONAL:
      self.startCharacters = b'-0123456789'
    elif valueSignType == DecimalFloatValueModelElement.SIGN_TYPE_MANDATORY:
      self.startCharacters = b'+-'
    else:
      raise Exception('Invalid valueSignType "%s"' % valueSignType)

    self.padCharacters = b''
    if valuePadType == DecimalFloatValueModelElement.PAD_TYPE_NONE:
      pass
    elif valuePadType == DecimalFloatValueModelElement.PAD_TYPE_ZERO:
      self.padCharacters = b'0'
    elif valuePadType == DecimalFloatValueModelElement.PAD_TYPE_BLANK:
      self.padCharacters = b' '
    else:
      raise Exception('Invalid valuePadType "%s"' % valueSignType)
    self.valuePadType = valuePadType

    if exponentType not in [
        DecimalFloatValueModelElement.EXP_TYPE_NONE,
        DecimalFloatValueModelElement.EXP_TYPE_OPTIONAL,
        DecimalFloatValueModelElement.EXP_TYPE_MANDATORY]:
      raise Exception('Invalid exponentType "%s"' % exponentType)
    self.exponentType = exponentType

  def getChildElements(self):
    """Get all possible child model elements of this element.
    @return empty list as there are no children of this element."""
    return None

  def getMatchElement(self, path, matchContext):
    """Find the maximum number of bytes forming a decimal number
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

# See if there is decimal part after decimal point.
    if (matchLen < len(data)) and (chr(data[matchLen]) == '.'):
      matchLen += 1
      postPointStart = matchLen
      for testByte in data[matchLen:]:
        if testByte not in b'0123456789':
          break
        matchLen += 1
      if matchLen == postPointStart:
# There has to be at least one digit after the decimal point.
        return None

# See if there could be any exponent following the number.
    if ((self.exponentType != DecimalFloatValueModelElement.EXP_TYPE_NONE) and
        (matchLen+1 < len(data)) and (data[matchLen] in b'eE')):
      matchLen += 1
      if data[matchLen] in b'+-':
        matchLen += 1
      expNumberStart = matchLen
      for testByte in data[matchLen:]:
        if testByte not in b'0123456789':
          break
        matchLen += 1
      if matchLen == expNumberStart:
# No exponent number found.
        return None

    matchString = data[:matchLen]
    matchValue = float(matchString)
    matchContext.update(matchString)
    return MatchElement(
        '%s/%s' % (path, self.pathId), matchString, matchValue, None)
