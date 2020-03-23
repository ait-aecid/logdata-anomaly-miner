"""This module defines a parser for syslog."""

from aminer.parsing import Datetime_modelElement
from aminer.parsing import FixedDataModelElement
from aminer.parsing import SequenceModelElement
from aminer.parsing import VariableByteDataModelElement

def get_model(time_model=None):
  """This function defines the model for parsing a standard syslog
  preamble including timestamp and hostname.
  @param time_model when not none, the given model element is used
  for parsing timestamps. Otherwise a standard Datetime_modelElement
  with format b'%b %d %H:%M:%S' is created. CAVEAT: the standard
  model may not work when log data timestamp locale does not match
  host or shell environment locale. See MultiLocaleDatetime_modelElement
  instead.
  """
  if time_model is None:
    time_model = Datetime_modelElement('time', b'%b %d %H:%M:%S')
  host_name_model = VariableByteDataModelElement('host', b'-.01234567890abcdefghijklmnopqrstuvwxyz')
  model = SequenceModelElement('syslog', [
      time_model,
      FixedDataModelElement('sp0', b' '),
      host_name_model,
      FixedDataModelElement('sp1', b' ')])
  return model
