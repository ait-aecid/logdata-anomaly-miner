import MatchElement

class IpAddressDataModelElement:
  def __init__(self, id):
    self.id=id

  def getChildElements(self):
    return(None)

  """Read an IP address at the current data position."""
  def getMatchElement(self, path, matchContext):
    data=matchContext.matchData

    numberCount=0
    digitCount=0
    matchLen=0
    extractedAddress=''
    for testByte in data:
      matchLen+=1
      if testByte in '0123456789':
        digitCount+=1
        continue
      if digitCount==0:
        return(None)

      extractedAddress+=str(int(data[matchLen-digitCount-1:matchLen-1]))
      digitCount=0
      numberCount+=1
      if (testByte!='.') or (numberCount==4):
        matchLen-=1
        break
      extractedAddress+='.'

    if digitCount!=0:
      extractedAddress+=str(int(data[matchLen-digitCount:matchLen]))

    matchString=data[:matchLen]
    matchContext.update(matchString)
    return(MatchElement.MatchElement("%s/%s" % (path, self.id),
        matchString, extractedAddress, None))
