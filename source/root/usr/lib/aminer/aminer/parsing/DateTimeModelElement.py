import datetime
import pytz
import sys

import MatchElement

class DateTimeModelElement:
  """This class defines a model element to parse date or datetime
  values of fixed length. Common formats are:
  * '%b %d %H:%M:%S' e.g. for 'Nov 19 05:08:43'"""
  def __init__(self, id, dateFormat, dateDataLength, formatHasYearFlag, startYear=None):
    self.id=id
    self.syslogTimeZone=pytz.timezone('UTC')
    self.dateFormat=dateFormat
    self.pythonYearParsingWorkaroundFormat=None
    self.pythonYearParsingWorkaroundLastDatetime=None
    self.dateDataLength=dateDataLength
    self.formatHasYearFlag=formatHasYearFlag
    self.startYear=startYear
    self.totalSecondsStartTime=datetime.datetime(1970,1,1)
    if not(formatHasYearFlag):
      if startYear==None:
        self.startYear=datetime.datetime.now().year
      self.pythonYearParsingWorkaroundFormat=dateFormat+' %Y'
      self.pythonYearParsingWorkaroundLastDatetime=datetime.datetime(self.startYear, 1, 1)

  def getChildElements(self):
    return(None)

  def getMatchElement(self, path, matchContext):
    """@return None when there is no match, MatchElement otherwise.
    The matchObject returned is a tuple containing the datetime
    object and the seconds since 1970"""
    data=matchContext.matchData
    if len(data) < self.dateDataLength: return(None)
    dateStr=data[0:self.dateDataLength]
    try:
      if self.formatHasYearFlag:
        parsedDateTime=datetime.datetime.strptime(dateStr, self.dateFormat)
      else:
# Python is too dumb to have leap-year aware parsing of semi-qualified
# dates. Use the inefficient workaround with startYear. Without
# any year information and completely unsorted logs, this will
# cause year number to increase quickly.
        parsedDateTime=datetime.datetime.strptime('%s %d' % (dateStr, self.startYear), self.pythonYearParsingWorkaroundFormat)
# Avoid timedelta.total_seconds(), not supported in Python 2.6.
        delta=(parsedDateTime-self.pythonYearParsingWorkaroundLastDatetime)
        if (delta.days*86400+delta.seconds+delta.microseconds)<-3600*24*7:
          print >>sys.stderr, 'WARNING: DateTimeModelElement unqualified timestamp year wraparound detected from %s to %s' % (self.pythonYearParsingWorkaroundLastDatetime, dateStr)
          parsedDateTime=parsedDateTime.replace(parsedDateTime.year+1)
          self.startYear+=1
        self.pythonYearParsingWorkaroundLastDatetime=parsedDateTime
    except:
      return(None)

# Avoid timedelta.total_seconds(), not supported in Python 2.6.
    delta=(parsedDateTime-self.totalSecondsStartTime)
    totalSeconds=(delta.days*86400+delta.seconds+delta.microseconds)
    matchContext.update(dateStr)
    return(MatchElement.MatchElement("%s/%s" % (path, self.id),
        dateStr, (parsedDateTime, totalSeconds,), None))
