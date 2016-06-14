import MatchElement

class IpAddressDataModelElement:
  def __init__(self, id):
    """Create an element to match IPv4 IP addresses."""
    self.id=id

  def getChildElements(self):
    return(None)

  def getMatchElement(self, path, matchContext):
    """Read an IP address at the current data position. When found,
    the matchObject will be """
    data=matchContext.matchData

    numberCount=0
    digitCount=0
    matchLen=0
    extractedAddress=0
    for testByte in data:
      matchLen+=1
      if testByte in '0123456789':
        digitCount+=1
        continue
      if digitCount==0:
        return(None)

      ipBits=int(data[matchLen-digitCount-1:matchLen-1])
      if ipBits>0xff:
        return(None)
      extractedAddress=(extractedAddress<<8)|ipBits
      digitCount=0
      numberCount+=1
      if numberCount==4:
# We are now after the first byte not belonging to the IP. So
# go back one step
        matchLen-=1
        break
      if (testByte!='.'):
        return(None)

    if digitCount!=0:
      ipBits=int(data[matchLen-digitCount:matchLen])
      if ipBits>0xff:
        return(None)
      extractedAddress=(extractedAddress<<8)|ipBits

    matchString=data[:matchLen]
    matchContext.update(matchString)
    return(MatchElement.MatchElement("%s/%s" % (path, self.id),
        matchString, extractedAddress, None))
