"""This module defines a parser for syslog."""

from aminer.parsing import DateTimeModelElement
from aminer.parsing import FixedDataModelElement
from aminer.parsing import SequenceModelElement
from aminer.parsing import VariableByteDataModelElement

def getModel(timeModel=None):
  """This function defines the model for parsing a standard syslog
  preamble including timestamp and hostname.
  @param timeModel when not none, the given model element is used
  for parsing timestamps. Otherwise a standard DateTimeModelElement
  with format b'%b %d %H:%M:%S' is created. CAVEAT: the standard
  model may not work when log data timestamp locale does not match
  host or shell environment locale. See MultiLocaleDateTimeModelElement
  instead.
  """
  if timeModel is None:
    timeModel = DateTimeModelElement('time', b'%b %d %H:%M:%S')
  hostNameModel = VariableByteDataModelElement('host', b'-.01234567890abcdefghijklmnopqrstuvwxyz')
  model = SequenceModelElement('syslog', [
      timeModel,
      FixedDataModelElement('sp0', b' '),
      hostNameModel,
      FixedDataModelElement('sp1', b' ')])
  return model
