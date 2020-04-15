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

  def __init__(self, element_id, date_formats, start_year=None):
    """Create a new MultiLocaleDateTimeModelElement object.
    @param date_formats this parameter is a list of tuples, each
    tuple containing information about one date format to support.
    The tuple structure is (format_string, format_locale, format_timezone).
    The format_string may contain the same elements as supported
    by strptime from datetime.datetime. The format_locale defines
    the locale for the string content, e.g. de_DE for german,
    but also the data IO encoding, e.g. ISO-8859-1. The locale
    information has to be available, e.g. using "locale-gen" on
    Debian systems. The format_timezone can be used to define the
    timezone of the timestamp parsed. When None, UTC is used.
    The timezone support may only be sufficient for very simple
    usecases, e.g. all data from one source configured to create
    timestamps in that timezone. This may still fail, e.g. when
    daylight savings changes make timestamps ambiguous during
    a short window of time. In all those cases, timezone should
    be left empty here and a separate filtering component should
    be used to apply timestamp corrections afterwards. See the
    FIXME-Filter component for that.
    Also having the same format_string for two different timezones
    will result in an error as correct timezone to apply cannot
    be distinguished just from format.
    @param start_year when given, parsing will use this year value
    for semiqualified timestamps to add correct year information.
    This is especially relevant for historic datasets as otherwise
    leap year handling may fail. The startYear parameter will
    only take effect when the first timestamp to be parsed by
    this object is also semiqualified. Otherwise the year information
    is extracted from this record. When empty and first parsing
    invocation involves a semiqualified date, the current year
    in UTC timezone is used."""
    self.element_id = element_id
    self.start_year = start_year
# The latest parsed timestamp value.
    self.latest_parsed_timestamp = None
    self.total_seconds_start_time = datetime.datetime(1970, 1, 1)

    self.date_formats = DateFormatComponent(-1, None, -1, None, None)
    default_locale = locale.getlocale()
# Build a decision tree for all format variants describing how
# to analyze a given timestamp. The tree is created containing
# nodes of form (separator, digitsOnlyFlag, length)
    for format_string, format_locale, format_timezone in date_formats:
      self.date_formats.add_format(format_string, format_locale, format_timezone)
# Restore previous locale settings. There seems to be no way in
# python to get back to the exact same state. Hence perform the
# reset only when locale has changed. This would also change the
# locale from (None, None) to some system-dependent locale.
    if locale.getlocale() != default_locale:
      locale.resetlocale()

  def get_child_elements(self):
    """Get all possible child model elements of this element.
    @return empty list as there are no children of this element."""
    return None


  def get_match_element(self, path, match_context):
    """This method checks if the data to match within the content
    is suitable to be parsed by any of the supplied date formats.
    @return On match return a matchObject containing a tuple of
    the datetime object and the seconds since 1970. When not matching,
    None is returned. When the timestamp data parsed would be
    far off from the last ones parsed, so that correction may
    not be applied correctly, then the method will also return
    None."""

    delta_string = 'Delta to last timestamp out of range for %s'
# Convert the head of the match_data to a timestamp value.
    parsed_data = self.date_formats.parse(match_context.match_data, 0)
    if parsed_data is None:
      return None
    parsed_fields = parsed_data[0]
    time_zone_info = parsed_data[2]

    date_str = match_context.match_data[0:parsed_data[1]]
    if parsed_fields[COMPONENT_TYPE_MICROSECOND] is None:
      parsed_fields[COMPONENT_TYPE_MICROSECOND] = 0

# FIXME: Values without day/month not handled yet
    parsed_value = None
    if parsed_fields[COMPONENT_TYPE_YEAR] is None:
      if self.latest_parsed_timestamp is not None:
        parsed_fields[COMPONENT_TYPE_YEAR] = self.latest_parsed_timestamp.year
      elif self.start_year is not None:
        parsed_fields[COMPONENT_TYPE_YEAR] = self.start_year
      else:
        parsed_fields[COMPONENT_TYPE_YEAR] = datetime.datetime.utcnow().year
    if parsed_fields[COMPONENT_TYPE_MONTH] is None:
      parsed_fields[COMPONENT_TYPE_MONTH] = 1
    if parsed_fields[COMPONENT_TYPE_DAY] is None:
      parsed_fields[COMPONENT_TYPE_DAY] = 1
    if parsed_fields[COMPONENT_TYPE_HOUR] is None:
      parsed_fields[COMPONENT_TYPE_HOUR] = 0
    if parsed_fields[COMPONENT_TYPE_MINUTE] is None:
      parsed_fields[COMPONENT_TYPE_MINUTE] = 0
    if parsed_fields[COMPONENT_TYPE_SECOND] is None:
      parsed_fields[COMPONENT_TYPE_SECOND] = 0
# Around new year, the year correction could change a semiqualified
# date to the beginning of the year or could change a semiqualified
# date lagging behind the latest date seen to the end of the following
# year.
      parsed_value = datetime.datetime(parsed_fields[COMPONENT_TYPE_YEAR], \
          parsed_fields[COMPONENT_TYPE_MONTH], \
          parsed_fields[COMPONENT_TYPE_DAY], \
          parsed_fields[COMPONENT_TYPE_HOUR], \
          parsed_fields[COMPONENT_TYPE_MINUTE], \
          parsed_fields[COMPONENT_TYPE_SECOND], \
          parsed_fields[COMPONENT_TYPE_MICROSECOND], \
          time_zone_info)
      if not self.checkTimestampValueInRange(parsed_value):
        parsed_value = datetime.datetime(parsed_fields[COMPONENT_TYPE_YEAR]+1, \
            parsed_fields[COMPONENT_TYPE_MONTH], \
            parsed_fields[COMPONENT_TYPE_DAY], \
            parsed_fields[COMPONENT_TYPE_HOUR], \
            parsed_fields[COMPONENT_TYPE_MINUTE], \
            parsed_fields[COMPONENT_TYPE_SECOND], \
            parsed_fields[COMPONENT_TYPE_MICROSECOND], \
            time_zone_info)
        if not self.checkTimestampValueInRange(parsed_value):
          parsed_value = datetime.datetime(parsed_fields[COMPONENT_TYPE_YEAR]-1, \
              parsed_fields[COMPONENT_TYPE_MONTH], \
              parsed_fields[COMPONENT_TYPE_DAY], \
              parsed_fields[COMPONENT_TYPE_HOUR], \
              parsed_fields[COMPONENT_TYPE_MINUTE], \
              parsed_fields[COMPONENT_TYPE_SECOND], \
              parsed_fields[COMPONENT_TYPE_MICROSECOND], \
              time_zone_info)
          if not self.checkTimestampValueInRange(parsed_value):
            print(delta_string % repr(date_str), file=sys.stderr)
            return None

      self.checkTimestampValueInRange(parsed_value)
      if self.latest_parsed_timestamp is not None:
        delta = (parsed_value - self.latest_parsed_timestamp)
        delta_seconds = (delta.days*86400+delta.seconds+delta.microseconds/1000)
        if (delta_seconds < -86400) or (delta_seconds > 86400*30):
          print(delta_string % repr(date_str), file=sys.stderr)
          return None

    else:
      parsed_value = datetime.datetime(parsed_fields[COMPONENT_TYPE_YEAR], \
          parsed_fields[COMPONENT_TYPE_MONTH], \
          parsed_fields[COMPONENT_TYPE_DAY], \
          parsed_fields[COMPONENT_TYPE_HOUR], \
          parsed_fields[COMPONENT_TYPE_MINUTE], \
          parsed_fields[COMPONENT_TYPE_SECOND], \
          parsed_fields[COMPONENT_TYPE_MICROSECOND], \
          time_zone_info)
      if not self.checkTimestampValueInRange(parsed_value):
        print(delta_string % repr(date_str), file=sys.stderr)
        return None

    self.total_seconds_start_time = datetime.datetime(1970, 1, 1, tzinfo=parsed_value.tzinfo)
    match_context.update(date_str)
    delta = (parsed_value - self.total_seconds_start_time)
    total_seconds = (delta.days*86400+delta.seconds+delta.microseconds/1000)+parsed_value.utcoffset().total_seconds()
    if (self.latest_parsed_timestamp is None) or (self.latest_parsed_timestamp < parsed_value):
      self.latest_parsed_timestamp = parsed_value
    return MatchElement("%s/%s" % (path, self.element_id), date_str, total_seconds, None)


  def checkTimestampValueInRange(self, parsed_value):
    """Return True if value is None."""
    if self.latest_parsed_timestamp is None:
      return True
    delta = (self.latest_parsed_timestamp - parsed_value)
    delta_seconds = (delta.days*86400+delta.seconds+delta.microseconds/1000)
    return (delta_seconds >= -86400) and (delta_seconds < 86400*30)



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
  def __init__(self, component_type, end_separator, component_length,
               translation_dictionary, parent_component):
    """Create the component object.
    @param end_separator when not none, this component is separated
    from the next by the given separator.
    @param component_length length of component for fixed length
    components, 0 otherwise.
    @param translation_dictionary a dictionary describing how
    the bytes of a formatted date component should be translated
    into a number by plain lookup. When None, the component will
    be treated as normal number."""
    self.component_type = component_type
    if (end_separator is not None) and not end_separator:
      raise Exception('Invalid zero-length separator string')
    self.end_separator = end_separator
    if (end_separator is None) and (component_length == 0) and (translation_dictionary is None):
      raise Exception('Invalid parameters to determine the length of the field')
    self.component_length = component_length
    self.translation_dictionary = translation_dictionary
    self.parent_component = parent_component
    self.format_timezone = None
    self.next_components = {}


  def add_format(self, format_string, format_locale, format_timezone):
    """Add a new format to be parsed."""
    if isinstance(format_string, bytes):
      format_string = format_string.decode('utf-8')
    if format_timezone is None:
      format_timezone = 'UTC'
    
    if format_string[0] != '%':
      raise Exception('Format string has to start with "%", strip away all static data outside \
        this formatter before starting to parse')
    if self.format_timezone is not None:
      raise Exception('Current node is already an end node, no format adding any more')

    parse_pos = 1
    component_type = -1
    component_length = -1
    translation_dictionary = None
    if format_string[parse_pos] == 'b' or format_string[parse_pos] == 'B':
# Month name
      parse_pos += 1
      component_type = COMPONENT_TYPE_MONTH
      component_length = 0
      locale.setlocale(locale.LC_ALL, format_locale)
      translation_dictionary = {}
      for month_num in range(1, 13):
# As we have switched locale before, this will return the byte
# string for the month name encoded using the correct encoding.
        new_value = datetime.datetime(1970, month_num, 1).strftime('%' + format_string[parse_pos - 1])
        for old_value in translation_dictionary:
          if (old_value.startswith(new_value)) or (new_value.startswith(old_value)):
            raise Exception('Strange locale with month names too similar')
        translation_dictionary[new_value] = month_num
      if len(translation_dictionary) != 12:
        raise Exception('Internal error: less than 12 month a year')
    elif format_string[parse_pos] == 'd':
# Day number
      parse_pos += 1
      component_type = COMPONENT_TYPE_DAY
      component_length = 2
    elif format_string[parse_pos] == 'H':
# Hour 0..23
      parse_pos += 1
      component_type = COMPONENT_TYPE_HOUR
      component_length = 2
    elif format_string[parse_pos] == 'M':
# Minute
      parse_pos += 1
      component_type = COMPONENT_TYPE_MINUTE
      component_length = 2
    elif format_string[parse_pos] == 'S':
# Second
      parse_pos += 1
      component_type = COMPONENT_TYPE_SECOND
      component_length = 2
    elif format_string[parse_pos] == 'Y':
# Year
      parse_pos += 1
      component_type = COMPONENT_TYPE_YEAR
      component_length = 4
    elif format_string[parse_pos] == 'm':
# Month
      parse_pos += 1
      component_type = COMPONENT_TYPE_MONTH
      component_length = 2
    elif format_string[parse_pos] == 'f':
# Microseconds
      parse_pos += 1
      component_type = COMPONENT_TYPE_MICROSECOND
      component_length = 6
    else:
      raise Exception('Unsupported date format code "%s"' % format_string[parse_pos])

    end_pos = format_string.find('%', parse_pos)
    end_separator = None
    if end_pos < 0:
      end_separator = format_string[parse_pos:]
      parse_pos = len(format_string)
    else:
      end_separator = format_string[parse_pos:end_pos]
      parse_pos = end_pos
    if not end_separator:
      end_separator = None

# Make sure all values are sane.

# Make sure no parent component is parsing the same type.
    check_component = self
    while check_component is not None:
      if check_component.component_type == component_type:
        raise Exception('Current format defines component of type %d twice' %
                        component_type)
      check_component = check_component.parent_component

    lookup_key = None
    if translation_dictionary is None:
      lookup_key = '%sn%d' % (end_separator, component_length)
    else:
      lookup_key = '%st%d' % (end_separator, component_length)
      
    if end_separator is not None:
      end_separator = end_separator.encode()

    next_component = self.next_components.get(lookup_key, None)
    if next_component is None:
      next_component = DateFormatComponent(component_type, end_separator, \
          component_length, translation_dictionary, self)
      self.next_components[lookup_key] = next_component
    else:
# Merge needed.
      next_component.mergeComponentData(component_type, component_length, \
          translation_dictionary)

    if parse_pos != len(format_string):
      next_component.add_format(format_string[parse_pos:], format_locale, \
                                format_timezone)
    else:
# Import in constructor to avoid failures reading the class in
# module initialization on setups without pytz.
      import pytz
      next_component.make_end_node(pytz.timezone(format_timezone))


  def merge_component_data(self, component_type, component_length,
                           translation_dictionary):
    """Merge data of given component type, length and lookup information
    into the current dataset."""
    if (self.component_type != component_type) or (self.component_length != component_length):
      raise Exception('Cannot merge data with different type or length')
    if (self.translation_dictionary is not None) != (translation_dictionary is not None):
      raise Exception('Cannot merge digit and translated data')
    if translation_dictionary is None:
# Without dictionary, we are done here: length and type are matching.
      return

    for key in translation_dictionary:
      for old_key in self.translation_dictionary:
        if ((key.startswith(old_key)) or (old_key.startswith(key))) and (key != old_key):
          raise Exception('Translation strings from different locales too similar for \
            unambiguous parsing')
      value = translation_dictionary.get(key)
      current_value = self.translation_dictionary.get(key, None)
      if current_value is None:
        self.translation_dictionary[key] = value
      elif current_value != value:
        raise Exception('Conflict in translation dictionary for %s: %s vs %s' % (
            key, value, current_value))


  def make_end_node(self, format_timezone):
    """Make this DateFormatComponent an end node. When reached
    during parsing, calculation of the timestamp value within
    the given is triggered."""
    if (self.format_timezone is not None) and (self.format_timezone != format_timezone):
      raise Exception('Node is already an end node for different timezone')
    elif self.next_components:
      raise Exception('Cannot make node with subcomponents an end node')
    self.format_timezone = format_timezone


  def parse(self, date_string, parse_pos):
    """Parse the supplied dateString starting from the given position.
    @return a triple containing the field list, the parsing end
    position and the target timezone for parsed fields."""

    component_value = None
# Position after value the value but before an optional separator.
    end_pos = -1
    if self.component_type >= 0:
      if self.end_separator is not None:
        if self.component_length == 0:
          end_pos = date_string.find(self.end_separator, parse_pos)
        else:
          end_pos = parse_pos + self.component_length
          if not date_string.find(self.end_separator, end_pos):
            end_pos = -1
        if end_pos < 0:
          return None
      elif self.component_length != 0:
        end_pos = parse_pos + self.component_length
      else:
        return None

      if end_pos != -1:
        value_str = date_string[parse_pos:end_pos]
        if self.translation_dictionary is None:
          try:
            component_value = int(value_str.strip())
          except ValueError:
            return None
        else:
          component_value = self.translation_dictionary.get(value_str.decode())
          if component_value is None:
            return None
      else:
# Without length, we need to got through all the dictionary components
# and see if the dateString starts with that key. As keys were
# already verified, that no key is starting portion of other key,
# that does not need to be checked.
        check_string = date_string[parse_pos:]
        for key in self.translation_dictionary:
          if check_string.startswith(key):
            component_value = self.translation_dictionary.get(key)
            end_pos = parse_pos + len(key)
            break
        if component_value is None:
          return None

# Now after parsing of value, add the length of the separator
# but make sure, it is really present.
      if self.end_separator is not None:
        if date_string.find(self.end_separator, end_pos) != end_pos:
          return None
        end_pos += len(self.end_separator)

    else:
# Negative componentType means, that this node is just a collector
# of subcomponents so do not change the parsing position for the
# next round.
      end_pos = 0

    if self.format_timezone is not None:
# This is the end node, return the results.
      fields = [None]*COMPONENT_TYPE_LENGTH
      fields[self.component_type] = component_value
      return (fields, end_pos, self.format_timezone)

# So this is no end node. Search the list of next components and
# continue parsing the next component.
    for key in self.next_components:
      next_component = self.next_components.get(key)
      result = next_component.parse(date_string, end_pos)
      if result is not None:
        if component_value is not None:
          result[0][self.component_type] = component_value
        return result
    return None
