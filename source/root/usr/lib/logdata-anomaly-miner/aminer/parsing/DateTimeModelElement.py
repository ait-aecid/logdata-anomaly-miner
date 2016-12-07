import datetime
import sys
import time

import MatchElement

class DateTimeModelElement:
  """This class defines a model element to parse date or datetime
  values. The element is similar to the strptime function but
  does not use it due to the numerous problems associated with
  it, e.g. no leap year support for semiqualified years, no %s
  (seconds since epoch) format in Python strptime, no %f support
  in libc strptime, no support to determine the length of the
  parsed string."""

  def __init__(self, id, dateFormat, timeZone=None, textLocale=None, startYear=None):
    """Create a DateTimeModelElement to parse dates using a custom,
    timezone and locale-aware implementation similar to strptime.
    @param dateFormat the date format for parsing, see Python
    strptime specification for available formats. Supported format
    specifiers are:
    * %b: month name in current locale
    * %d: day in month, can be space or zero padded when followed
      by separator or at end of string.
    * %f: fraction of seconds (the digits after the the '.')
    * %H: hours from 00 to 23
    * %M: minutes
    * %m: two digit month number
    * %S: seconds
    * %s: seconds since the epoch (1970-01-01)
    * %Y: 4 digit year number
    Common formats are:
    * '%b %d %H:%M:%S' e.g. for 'Nov 19 05:08:43'
    @param timeZone the timezone for parsing the values or UTC
    when None.
    @param textLocale the locale to use for parsing the day, month
    names."""
    self.id=id
    self.timeZone=timeZone
# Make sure that dateFormat is valid and extract the relevant
# parts from it.
    self.formatHasYearFlag=False
    dateFormatParts=[]
    dateFormatTypeSet=set()
    scanPos=0
    while scanPos<len(dateFormat):
      nextParamPos=dateFormat.find('%', scanPos)
      if nextParamPos<0: nextParamPos=len(dateFormat)
      newElement=None
      if nextParamPos!=scanPos:
        newElement=dateFormat[scanPos:nextParamPos]
      else:
        paramTypeCode=dateFormat[nextParamPos+1]
        nextParamPos=scanPos+2
        if paramTypeCode=='%':
          newElement='%'
        elif paramTypeCode=='b':
          import calendar
          nameDict={}
          for monthPos in range(1, 13):
            nameDict[calendar.month_name[monthPos][:3]]=monthPos
          newElement=(1, 3, nameDict)
        elif paramTypeCode=='d':
          newElement=(2, 2, int)
        elif paramTypeCode=='f':
          newElement=(6, -1, DateTimeModelElement.parseFraction)
        elif paramTypeCode=='H':
          newElement=(3, 2, int)
        elif paramTypeCode=='M':
          newElement=(4, 2, int)
        elif paramTypeCode=='m':
          newElement=(1, 2, int)
        elif paramTypeCode=='S':
          newElement=(5, 2, int)
        elif paramTypeCode=='s':
          newElement=(7, -1, int)
        elif paramTypeCode=='Y':
          newElement=(0, 4, int)
        else:
          raise Exception('Unknown dateformat specifier %s' % repr(paramTypeCode))
      if isinstance(newElement, str):
        if (len(dateFormatParts)>0) and (isinstance(dateFormatParts[-1], str)):
          dateFormatParts[-1]+=newElement
        else:
          dateFormatParts.append(newElement)
      else:
        if newElement[0] in dateFormatTypeSet:
          raise Exception('Multiple format specifiers for type %d' % newElement[0])
        dateFormatTypeSet.add(newElement[0])
        dateFormatParts.append(newElement)
      scanPos=nextParamPos
    if (7 in dateFormatTypeSet) and (not(dateFormatTypeSet.isdisjoint(set(range(0, 6))))):
      raise Exception('Cannot use %%s (seconds since epoch) with other non-second format types')
    self.dateFormatParts=dateFormatParts

    self.startYear=startYear
    if (not(self.formatHasYearFlag)) and (startYear==None):
      self.startYear=time.gmtime(None).tm_year
    self.lastParsedSeconds=0
    self.epochStartTime=datetime.datetime.fromtimestamp(0, self.timeZone)

  def getChildElements(self):
    return(None)

  def getMatchElement(self, path, matchContext):
    """@return None when there is no match, MatchElement otherwise.
    The matchObject returned is a tuple containing the datetime
    object and the seconds since 1970"""
    parsePos=0
# Year, month, day, hour, minute, second, fraction, gmt-seconds:
    result=[None, None, None, None, None, None, None, None]
    for partPos in range(0, len(self.dateFormatParts)):
      dateFormatPart=self.dateFormatParts[partPos]
      if isinstance(dateFormatPart, str):
        if not(matchContext.matchData[parsePos:].startswith(dateFormatPart)):
          return(None)
        parsePos+=len(dateFormatPart)
        continue
      nextLength=dateFormatPart[1]
      nextData=None
      if nextLength<0:
# No length given: this is only valid for integer fields or fields
# followed by a separator string.
        if (partPos+1)<len(self.dateFormatParts):
          nextPart=self.dateFormatParts[partPos+1]
          if isinstance(nextPart, str):
            endPos=matchContext.matchData.find(nextPart, parsePos)
            if endPos<0:
              return(None)
            nextLength=endPos-parsePos
        if nextLength<0:
# No separator, so get the number of decimal digits.
          nextLength=0
          for digitChar in matchContext.matchData[parsePos:]:
            digitOrd=ord(digitChar)
            if (digitOrd<0x30) or (digitOrd>0x39): break
            nextLength+=1
          if nextLength==0:
            return(None)
        nextData=matchContext.matchData[parsePos:parsePos+nextLength]
      else:
        nextData=matchContext.matchData[parsePos:parsePos+nextLength]
        if len(nextData)!=nextLength:
          return(None)
      parsePos+=nextLength
      transformFunction=dateFormatPart[2]
      if isinstance(transformFunction, dict):
        value=None
        try:
          value=transformFunction.get(nextData, None)
        except ValueError as transformError:
          pass
        if value==None:
          return(None)
        result[dateFormatPart[0]]=value
      else:
        result[dateFormatPart[0]]=transformFunction(nextData)
    dateStr=matchContext.matchData[:parsePos]

# Now combine the values and build the final value.
    parsedDateTime=None
    totalSeconds=result[7]
    if totalSeconds!=None:
      if result[6]!=None:
        totalSeconds+=result[6]
# For epoch second formats, the datetime value usually is not
# important. So stay with parsedDateTime to none.
    else:
      if not(self.formatHasYearFlag):
        result[0]=self.startYear
      microseconds=0
      if result[6]!=None:
        microseconds=int(result[6]*1000000)
      try:
        parsedDateTime=datetime.datetime(result[0], result[1], result[2], result[3], result[4], result[5], microseconds, self.timeZone)
      except:
# The values did not form a valid datetime object, e.g. when the
# day of month is out of range. The rare case where dates without
# year are parsed and the last parsed timestamp was from the previous
# non-leap year but the current timestamp is it, is ignored. Values
# that sparse and without a year number are very likely to result
# in invalid data anyway.
        raise
        return(None)

# Avoid timedelta.total_seconds(), not supported in Python 2.6.
      delta=parsedDateTime-self.epochStartTime
      totalSeconds=(delta.days*86400+delta.seconds)

# See if this is change from one year to next.
      if (not(self.formatHasYearFlag)) and (totalSeconds<self.lastParsedSeconds-3600*24*7):
        print >>sys.stderr, 'WARNING: DateTimeModelElement unqualified timestamp year wraparound detected from %s to %s' % (datetime.datetime.fromtimestamp(self.lastParsedSeconds, self.timeZone).isoformat(), parsedDateTime.isoformat())
        self.startYear+=1
        parsedDateTime=parsedDateTime.replace(self.startYear)

      self.lastParsedSeconds=totalSeconds
# We discarded the parsedDateTime microseconds beforehand, use
# the full float value here instead of the rounded integer.
      if result[6]!=None:
        totalSeconds+=result[6]

    matchContext.update(dateStr)
    return(MatchElement.MatchElement("%s/%s" % (path, self.id),
        dateStr, (parsedDateTime, totalSeconds,), None))

  @staticmethod
  def parseFraction(str):
    """This method is just required to pass it as function pointer
    to the parsing logic."""
    return(float('0.'+str))
