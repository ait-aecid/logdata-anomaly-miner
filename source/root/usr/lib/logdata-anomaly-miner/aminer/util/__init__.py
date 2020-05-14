"""This module contains various methods and class definitions
useful for various components from parsing, analysis and event
handling. Larger separate blocks of code should be split into
own subfiles or submodules, e.g. persistency."""

import random

from aminer.input import AtomHandlerInterface
interface_method_called = 'Interface method called'


def get_log_int(max_bits):
  """Get a log-distributed random integer integer in range 0 to
  maxBits-1."""
  rand_bits = random.randint(0, (1 << max_bits) - 1)
  result = 0
  while (rand_bits & 1) != 0:
    result += 1
    rand_bits >>= 1
  return result


def decode_string_as_byte_string(string):
  """Decodes a string produced by the encode function
  encodeByteStringAsString(byteString) below.
  @return string."""
  decoded = b''
  count = 0
  while count < len(string):
    if string[count] in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRS' \
            'TUVWXYZ1234567890!"#$&\'()*+,-./:;<=>?@[]\\^_`' \
            '{}|~ ':
      decoded += bytes(string[count], 'ascii')
      count += 1
    elif string[count] == '%':
      decoded += bytearray((int(string[count+1:count+3], 16),))
      count += 3
    else:
      raise Exception('Invalid encoded character')
  return decoded


def encode_byte_string_as_string(byte_string):
  """Encodes an arbitrary byte string to a string by replacing
  all non ascii-7 bytes and all non printable ascii-7 bytes
  and % character by replacing with their escape sequence
  %[hex].
  For example byte string b'/\xc3' is encoded to '/%c3'
  @return a string with decoded name."""
  encoded = ''
  for byte in byte_string:
    if byte in b'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRS' \
            b'TUVWXYZ1234567890!"#$&\'()*+,-./:;<=>?@[]\\^_`' \
            b'{}|~ ':
      encoded += chr(byte)
    else:
      encoded += '%%%02x' % byte
  return encoded


class ObjectHistory:
  """This is the superinterface of all object histories. The idea
  behind that is to use that type of history best suited for a
  purpose considering amount of data, possibility for history
  size limits to be reached, priorization which elements should
  be dropped first."""

  # skipcq: PYL-R0201
  def add_object(self, new_object):
    """Add an object to this history. This method call may evict
    other objects from the history."""
    raise Exception(interface_method_called)

  # skipcq: PYL-R0201
  def get_history(self):
    """Get the whole history list. Make sure to clone the list
    before modification when influences on this object are not
    intended."""
    raise Exception(interface_method_called)

  # skipcq: PYL-R0201
  def clear_history(self):
    """Clean the whole history."""
    raise Exception(interface_method_called)


class LogarithmicBackoffHistory(ObjectHistory):
  """This class keeps a history list of items with logarithmic
  storage characteristics. When adding objects, the list will
  be filled to the maximum size with the newest items at the end.
  When filled, adding a new element will replace with probability
  1/2 the last element. With a chance of 1/4, the last element
  will be moved to the next lower position, before putting the
  new element at the end of the list. With a chance of 1/8, the
  last two elements are moved, ... Thus the list will in average
  span a time range of 2^maxItems items with growing size of 
  holes towards the earliest element."""

  def __init__(self, max_items, initial_list=None):
    self.max_items = max_items
    if initial_list is None:
      initial_list = []
    else:
      initial_list = initial_list[:max_items]
    self.history = initial_list

  def add_object(self, new_object):
    """Add a new object to the list according to the rules described
    in the class docstring."""
    if len(self.history) < self.max_items:
      self.history.append(new_object)
    else:
      move_pos = get_log_int(self.max_items - 1)
      self.history = self.history[:self.max_items - move_pos - 1] + \
                     self.history[self.max_items - move_pos:] + [new_object]

  def get_history(self):
    """Get the whole history list. Make sure to clone the list
    before modification when influences on this object are not
    intended."""
    return self.history

  def clear_history(self):
    """Clean the whole history."""
    self.history[:] = []


class TimeTriggeredComponentInterface:
  """This is the common interface of all components that can be
  registered to receive timer interrupts. There might be different
  timelines for triggering, real time and normalized log data
  time scale for forensic analysis. For forensic analyis different
  timers might be available to register a component. Therefore
  the component should state, which type of triggering it would
  require."""

  # skipcq: PYL-R0201
  def get_time_trigger_class(self):
    """Get the trigger class this component can be registered
    for. See AnalysisContext class for different trigger classes
    available."""
    raise Exception(interface_method_called)

  # skipcq: PYL-R0201
  def do_timer(self, trigger_time):
    """This method is called to perform trigger actions and to
    determine the time for next invocation. The caller may decide
    to invoke this method earlier than requested during the previous
    call. Classes implementing this method have to handle such
    cases. Each class should try to limit the time spent in this
    method as it might delay trigger signals to other components.
    For extensive compuational work or IO, a separate thread should
    be used.
    @param trigger_time the time this trigger is invoked. This
    might be the current real time when invoked from real time
    timers or the forensic log timescale time value.
    @return the number of seconds when next invocation of this
    trigger is required."""
    raise Exception(interface_method_called)


class VolatileLogarithmicBackoffAtomHistory(AtomHandlerInterface, LogarithmicBackoffHistory):
  """This class is a volatile filter to keep a history of log
  atoms, e.g. for analysis by other components or for external
  access via remote control interface."""

  def __init__(self, max_items):
    """Initialize the history component."""
    LogarithmicBackoffHistory.__init__(self, max_items)

  def receive_atom(self, log_atom):
    """Receive an atom and add it to the history log."""
    self.add_object(log_atom)
    return True
