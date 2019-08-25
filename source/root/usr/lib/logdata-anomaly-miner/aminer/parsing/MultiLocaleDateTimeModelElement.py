"""This module defines a model element representing date or
datetime from sources with different locales."""

import datetime
import locale
import sys

from aminer.parsing.MatchElement import MatchElement
from aminer.parsing import ModelElementInterface

class MultiLocaleDateTimeModelElement(ModelElementInterface):
  """This class defines a model element to parse date or datetime
  values from log sources containing timestamps encoded in different
  locales or on machines, where host/service locale does not match
  data locale(s).
  CAVEAT: Unlike other model elements, this element is not completely
  stateless! As parsing of semiqualified date values without any
  year information may produce wrong results, e.g. wrong year
  or 1 day off due to incorrect leap year handling, this object
  will keep track of the most recent timestamp parsed and will
  use it to regain information about the year in semiqualified
  date values. Still this element will not complain when parsed
  timestamp values are not strictly sorted, this should be done
  by filtering modules later on. The sorting requirements here
  are only, that each new timestamp value may not be more than
  2 days before and 1 month after the most recent one observer.

  Internal operation:
  * When creating the object, make sure that there are no ambiguous
    dateFormats in the list, e.g. one with "day month" and another
    one with "month day".
  * To avoid decoding of binary input data in all locales before
    searching for e.g. month names, convert all possible month
    names to bytes during object creation and just keep the lookup
    list."""

  def __init__(self, elementId, dateFormats, startYear=None):
    """Create a new MultiLocaleDateTimeModelElement object.
    @param dateFormats this parameter is a list of tuples, each
    tuple containing information about one date format to support.
    The tuple structure is (formatString, formatLocale, formatTimezone).
    The formatString may contain the same elements as supported
    by strptime from datetime.datetime. The formatLocale defines
    the locale for the string content, e.g. de_DE for german,
    but also the data IO encoding, e.g. ISO-8859-1. The locale
    information has to be available, e.g. using "locale-gen" on
    Debian systems. The formatTimezone can be used to define the
    timezone of the timestamp parsed. When None, UTC is used.
    The timezone support may only be sufficient for very simple
    usecases, e.g. all data from one source configured to create
    timestamps in that timezone. This may still fail, e.g. when
    daylight savings changes make timestamps ambiguous during
    a short window of time. In all those cases, timezone should
    be left empty here and a separate filtering component should
    be used to apply timestamp corrections afterwards. See the
    FIXME-Filter component for that.
    Also having the same formatString for two different timezones
    will result in an error as correct timezone to apply cannot
    be distinguished just from format.
    @param startYear when given, parsing will use this year value
    for semiqualified timestamps to add correct year information.
    This is especially relevant for historic datasets as otherwise
    leap year handling may fail. The startYear parameter will
    only take effect when the first timestamp to be parsed by
    this object is also semiqualified. Otherwise the year information
    is extracted from this record. When empty and first parsing
    invocation involves a semiqualified date, the current year
    in UTC timezone is used."""
    self.elementId = elementId
    self.startYear = startYear
# The latest parsed timestamp value.
    self.latestParsedTimestamp = None
    self.totalSecondsStartTime = datetime.datetime(1970, 1, 1)

    self.dateFormats = DateFormatComponent(-1, None, -1, None, None)
    defaultLocale = locale.getlocale()
# Build a decision tree for all format variants describing how
# to analyze a given timestamp. The tree is created containing
# nodes of form (separator, digitsOnlyFlag, length)
    for formatString, formatLocale, formatTimezone in dateFormats:
      self.dateFormats.addFormat(formatString, formatLocale, formatTimezone)
# Restore previous locale settings. There seems to be no way in
# python to get back to the exact same state. Hence perform the
# reset only when locale has changed. This would also change the
# locale from (None, None) to some system-dependent locale.
    if locale.getlocale() != defaultLocale:
      locale.resetlocale()

  def getChildElements(self):
    """Get all possible child model elements of this element.
    @return empty list as there are no children of this element."""
    return None


  def getMatchElement(self, path, matchContext):
    """This method checks if the data to match within the content
    is suitable to be parsed by any of the supplied date formats.
    @return On match return a matchObject containing a tuple of
    the datetime object and the seconds since 1970. When not matching,
    None is returned. When the timestamp data parsed would be
    far off from the last ones parsed, so that correction may
    not be applied correctly, then the method will also return
    None."""

# Convert the head of the matchData to a timestamp value.
    parsedData = self.dateFormats.parse(matchContext.matchData, 0)
    if parsedData is None:
      return None
    parsedFields = parsedData[0]
    timeZoneInfo = parsedData[2]

    dateStr = matchContext.matchData[0:parsedData[1]]
    if parsedFields[COMPONENT_TYPE_MICROSECOND] is None:
      parsedFields[COMPONENT_TYPE_MICROSECOND] = 0

# FIXME: Values without day/month not handled yet
    parsedValue = None
    if parsedFields[COMPONENT_TYPE_YEAR] is None:
      if self.latestParsedTimestamp is not None:
        parsedFields[COMPONENT_TYPE_YEAR] = self.latestParsedTimestamp.year
      elif self.startYear is not None:
        parsedFields[COMPONENT_TYPE_YEAR] = self.startYear
      else:
        parsedFields[COMPONENT_TYPE_YEAR] = datetime.datetime.utcnow().year
    if parsedFields[COMPONENT_TYPE_MONTH] is None:
      parsedFields[COMPONENT_TYPE_MONTH] = 1
    if parsedFields[COMPONENT_TYPE_DAY] is None:
      parsedFields[COMPONENT_TYPE_DAY] = 1
    if parsedFields[COMPONENT_TYPE_HOUR] is None:
      parsedFields[COMPONENT_TYPE_HOUR] = 0
    if parsedFields[COMPONENT_TYPE_MINUTE] is None:
      parsedFields[COMPONENT_TYPE_MINUTE] = 0
    if parsedFields[COMPONENT_TYPE_SECOND] is None:
      parsedFields[COMPONENT_TYPE_SECOND] = 0
# Around new year, the year correction could change a semiqualified
# date to the beginning of the year or could change a semiqualified
# date lagging behind the latest date seen to the end of the following
# year.
      parsedValue = datetime.datetime(parsedFields[COMPONENT_TYPE_YEAR], \
          parsedFields[COMPONENT_TYPE_MONTH], \
          parsedFields[COMPONENT_TYPE_DAY], \
          parsedFields[COMPONENT_TYPE_HOUR], \
          parsedFields[COMPONENT_TYPE_MINUTE], \
          parsedFields[COMPONENT_TYPE_SECOND], \
          parsedFields[COMPONENT_TYPE_MICROSECOND], \
          timeZoneInfo)
      if not self.checkTimestampValueInRange(parsedValue):
        parsedValue = datetime.datetime(parsedFields[COMPONENT_TYPE_YEAR]+1, \
            parsedFields[COMPONENT_TYPE_MONTH], \
            parsedFields[COMPONENT_TYPE_DAY], \
            parsedFields[COMPONENT_TYPE_HOUR], \
            parsedFields[COMPONENT_TYPE_MINUTE], \
            parsedFields[COMPONENT_TYPE_SECOND], \
            parsedFields[COMPONENT_TYPE_MICROSECOND], \
            timeZoneInfo)
        if not self.checkTimestampValueInRange(parsedValue):
          parsedValue = datetime.datetime(parsedFields[COMPONENT_TYPE_YEAR]-1, \
              parsedFields[COMPONENT_TYPE_MONTH], \
              parsedFields[COMPONENT_TYPE_DAY], \
              parsedFields[COMPONENT_TYPE_HOUR], \
              parsedFields[COMPONENT_TYPE_MINUTE], \
              parsedFields[COMPONENT_TYPE_SECOND], \
              parsedFields[COMPONENT_TYPE_MICROSECOND], \
              timeZoneInfo)
          if not self.checkTimestampValueInRange(parsedValue):
            print('Delta to last timestamp out of range for %s' % repr(dateStr), file=sys.stderr)
            return None

      self.checkTimestampValueInRange(parsedValue)
      if self.latestParsedTimestamp is not None:
        delta = (self.latestParsedTimestamp-self.latestParsedTimestamp)
        deltaSeconds = (delta.days*86400+delta.seconds+delta.microseconds/1000)
        if (deltaSeconds < -86400) or (deltaSeconds > 86400*30):
          print('Delta to last timestamp out of range for %s' % repr(dateStr), file=sys.stderr)
          return None

    else:
      parsedValue = datetime.datetime(parsedFields[COMPONENT_TYPE_YEAR], \
          parsedFields[COMPONENT_TYPE_MONTH], \
          parsedFields[COMPONENT_TYPE_DAY], \
          parsedFields[COMPONENT_TYPE_HOUR], \
          parsedFields[COMPONENT_TYPE_MINUTE], \
          parsedFields[COMPONENT_TYPE_SECOND], \
          parsedFields[COMPONENT_TYPE_MICROSECOND], \
          timeZoneInfo)
      if not self.checkTimestampValueInRange(parsedValue):
        print('Delta to last timestamp out of range for %s' % repr(dateStr), file=sys.stderr)
        return None

    self.totalSecondsStartTime = datetime.datetime(1970, 1, 1, tzinfo=parsedValue.tzinfo)
    matchContext.update(dateStr)
    delta = (parsedValue-self.totalSecondsStartTime)
    totalSeconds = (delta.days*86400+delta.seconds+delta.microseconds/1000)+parsedValue.utcoffset().total_seconds()
    if (self.latestParsedTimestamp is None) or (self.latestParsedTimestamp < parsedValue):
      self.latestParsedTimestamp = parsedValue
    return MatchElement("%s/%s" % (path, self.elementId), dateStr, (parsedValue, totalSeconds), \
            None)


  def checkTimestampValueInRange(self, parsedValue):
    """Return True if value is None."""
    if self.latestParsedTimestamp is None:
      return True
    delta = (self.latestParsedTimestamp-parsedValue)
    deltaSeconds = (delta.days*86400+delta.seconds+delta.microseconds/1000)
    return (deltaSeconds >= -86400) and (deltaSeconds < 86400*30)



COMPONENT_TYPE_YEAR = 0
COMPONENT_TYPE_MONTH = 1
COMPONENT_TYPE_DAY = 2
COMPONENT_TYPE_HOUR = 3
COMPONENT_TYPE_MINUTE = 4
COMPONENT_TYPE_SECOND = 5
COMPONENT_TYPE_MICROSECOND = 6
COMPONENT_TYPE_LENGTH = 7

class DateFormatComponent:
  """This class defines a component in the date format."""
  def __init__(self, componentType, endSeparator, componentLength,
               translationDictionary, parentComponent):
    """Create the component object.
    @param endSeparator when not none, this component is separated
    from the next by the given separator.
    @param componentLength length of component for fixed length
    components, 0 otherwise.
    @param translationDictionary a dictionary describing how
    the bytes of a formatted date component should be translated
    into a number by plain lookup. When None, the component will
    be treated as normal number."""
    self.componentType = componentType
    if (endSeparator is not None) and not endSeparator:
      raise Exception('Invalid zero-length separator string')
    self.endSeparator = endSeparator
    if (endSeparator is None) and (componentLength == 0) and (translationDictionary is None):
      raise Exception('Invalid parameters to determine the length of the field')
    self.componentLength = componentLength
    self.translationDictionary = translationDictionary
    self.parentComponent = parentComponent
    self.formatTimezone = None
    self.nextComponents = {}


  def addFormat(self, formatString, formatLocale, formatTimezone):
    """Add a new format to be parsed."""
    if isinstance(formatString, bytes):
      formatString = formatString.decode('utf-8')
    if formatTimezone is None:
      formatTimezone = 'UTC'
    
    if formatString[0] != '%':
      raise Exception('Format string has to start with "%", strip away all static data outside \
        this formatter before starting to parse')
    if self.formatTimezone is not None:
      raise Exception('Current node is already an end node, no format adding any more')

    parsePos = 1
    componentType = -1
    componentLength = -1
    translationDictionary = None
    if formatString[parsePos] == 'b' or formatString[parsePos] == 'B':
# Month name
      parsePos += 1
      componentType = COMPONENT_TYPE_MONTH
      componentLength = 0
      locale.setlocale(locale.LC_ALL, formatLocale)
      translationDictionary = {}
      for monthNum in range(1, 13):
# As we have switched locale before, this will return the byte
# string for the month name encoded using the correct encoding.
        newValue = datetime.datetime(1970, monthNum, 1).strftime('%'+formatString[parsePos-1])
        for oldValue in translationDictionary:
          if (oldValue.startswith(newValue)) or (newValue.startswith(oldValue)):
            raise Exception('Strange locale with month names too similar')
        translationDictionary[newValue] = monthNum
      if len(translationDictionary) != 12:
        raise Exception('Internal error: less than 12 month a year')
    elif formatString[parsePos] == 'd':
# Day number
      parsePos += 1
      componentType = COMPONENT_TYPE_DAY
      componentLength = 2
    elif formatString[parsePos] == 'H':
# Hour 0..23
      parsePos += 1
      componentType = COMPONENT_TYPE_HOUR
      componentLength = 2
    elif formatString[parsePos] == 'M':
# Minute
      parsePos += 1
      componentType = COMPONENT_TYPE_MINUTE
      componentLength = 2
    elif formatString[parsePos] == 'S':
# Second
      parsePos += 1
      componentType = COMPONENT_TYPE_SECOND
      componentLength = 2
    elif formatString[parsePos] == 'Y':
# Year
      parsePos += 1
      componentType = COMPONENT_TYPE_YEAR
      componentLength = 4
    elif formatString[parsePos] == 'm':
# Month
      parsePos += 1
      componentType = COMPONENT_TYPE_MONTH
      componentLength = 2
    elif formatString[parsePos] == 'f':
# Microseconds
      parsePos += 1
      componentType = COMPONENT_TYPE_MICROSECOND
      componentLength = 6
    else:
      raise Exception('Unsupported date format code "%s"' % formatString[parsePos])

    endPos = formatString.find('%', parsePos)
    endSeparator = None
    if endPos < 0:
      endSeparator = formatString[parsePos:].encode()
      parsePos = len(formatString)
    else:
      endSeparator = formatString[parsePos:endPos].encode()
      parsePos = endPos
    if not endSeparator:
      endSeparator = None

# Make sure all values are sane.

# Make sure no parent component is parsing the same type.
    checkComponent = self
    while checkComponent is not None:
      if checkComponent.componentType == componentType:
        raise Exception('Current format defines component of type %d twice' %
                        componentType)
      checkComponent = checkComponent.parentComponent

    lookupKey = None
    if translationDictionary is None:
      lookupKey = '%sn%d' % (endSeparator, componentLength)
    else:
      lookupKey = '%st%d' % (endSeparator, componentLength)

    nextComponent = self.nextComponents.get(lookupKey, None)
    if nextComponent is None:
      nextComponent = DateFormatComponent(componentType, endSeparator, \
          componentLength, translationDictionary, self)
      self.nextComponents[lookupKey] = nextComponent
    else:
# Merge needed.
      nextComponent.mergeComponentData(componentType, componentLength, \
          translationDictionary)

    if parsePos != len(formatString):
      nextComponent.addFormat(formatString[parsePos:], formatLocale, \
          formatTimezone)
    else:
# Import in constructor to avoid failures reading the class in
# module initialization on setups without pytz.
      import pytz
      nextComponent.makeEndNode(pytz.timezone(formatTimezone))


  def mergeComponentData(self, componentType, componentLength,
                         translationDictionary):
    """Merge data of given component type, length and lookup information
    into the current dataset."""
    if (self.componentType != componentType) or (self.componentLength != componentLength):
      raise Exception('Cannot merge data with different type or length')
    if (self.translationDictionary is not None) != (translationDictionary is not None):
      raise Exception('Cannot merge digit and translated data')
    if translationDictionary is None:
# Without dictionary, we are done here: length and type are matching.
      return

    for key in translationDictionary:
      for oldKey in self.translationDictionary:
        if ((key.startswith(oldKey)) or (oldKey.startswith(key))) and (key != oldKey):
          raise Exception('Translation strings from different locales too similar for \
            unambiguous parsing')
      value = translationDictionary.get(key)
      currentValue = self.translationDictionary.get(key, None)
      if currentValue is None:
        self.translationDictionary[key] = value
      elif currentValue != value:
        raise Exception('Conflict in translation dictionary for %s: %s vs %s' % (
            key, value, currentValue))


  def makeEndNode(self, formatTimezone):
    """Make this DateFormatComponent an end node. When reached
    during parsing, calculation of the timestamp value within
    the given is triggered."""
    if (self.formatTimezone is not None) and (self.formatTimezone != formatTimezone):
      raise Exception('Node is already an end node for different timezone')
    elif self.nextComponents:
      raise Exception('Cannot make node with subcomponents an end node')
    self.formatTimezone = formatTimezone


  def parse(self, dateString, parsePos):
    """Parse the supplied dateString starting from the given position.
    @return a triple containing the field list, the parsing end
    position and the target timezone for parsed fields."""

    componentValue = None
# Position after value the value but before an optional separator.
    endPos = -1
    if self.componentType >= 0:
      if self.endSeparator is not None:
        if self.componentLength == 0:
          endPos = dateString.find(self.endSeparator, parsePos)
        else:
          endPos = parsePos+self.componentLength
          if not dateString.find(self.endSeparator, endPos):
            endPos = -1
        if endPos < 0:
          return None
      elif self.componentLength != 0:
        endPos = parsePos+self.componentLength
      else:
        return None

      if endPos != -1:
        valueStr = dateString[parsePos:endPos]
        if self.translationDictionary is None:
          componentValue = int(valueStr.strip())
        else:
          componentValue = self.translationDictionary.get(valueStr.decode())
          if componentValue is None:
            return None
      else:
# Without length, we need to got through all the dictionary components
# and see if the dateString starts with that key. As keys were
# already verified, that no key is starting portion of other key,
# that does not need to be checked.
        checkString = dateString[parsePos:]
        for key in self.translationDictionary:
          if checkString.startswith(key):
            componentValue = self.translationDictionary.get(key)
            endPos = parsePos+len(key)
            break
        if componentValue is None:
          return None

# Now after parsing of value, add the length of the separator
# but make sure, it is really present.
      if self.endSeparator is not None:
        if dateString.find(self.endSeparator, endPos) != endPos:
          return None
        endPos += len(self.endSeparator)

    else:
# Negative componentType means, that this node is just a collector
# of subcomponents so do not change the parsing position for the
# next round.
      endPos = 0

    if self.formatTimezone is not None:
# This is the end node, return the results.
      fields = [None]*COMPONENT_TYPE_LENGTH
      fields[self.componentType] = componentValue
      return (fields, endPos, self.formatTimezone)

# So this is no end node. Search the list of next components and
# continue parsing the next component.
    for key in self.nextComponents:
      nextComponent = self.nextComponents.get(key)
      result = nextComponent.parse(dateString, endPos)
      if result is not None:
        if componentValue is not None:
          result[0][self.componentType] = componentValue
        return result
    return None


# Todos:
# * Add unit-test with
#   * leap year
#   * dst hour gain/loose
