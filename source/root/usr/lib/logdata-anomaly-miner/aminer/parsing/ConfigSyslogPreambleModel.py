import DateTimeModelElement
import FixedDataModelElement
import SequenceModelElement
import VariableByteDataModelElement

def getModel(timeModel=None):
  """This function defines the model for parsing a standard syslog
  preamble including timestamp and hostname.
  @param timeModel when not none, the given model element is used
  for parsing timestamps. Otherwise a standard DateTimeModelElement
  with format '%b %d %H:%M:%S' is created. CAVEAT: the standard
  model may not work when log data timestamp locale does not match
  host or shell environment locale. See MultiLocaleDateTimeModelElement
  instead.
  """
  if timeModel==None:
    timeModel=DateTimeModelElement.DateTimeModelElement('time', '%b %d %H:%M:%S', 15, False)
  hostNameModel=VariableByteDataModelElement.VariableByteDataModelElement('host', '-.01234567890abcdefghijklmnopqrstuvwxyz')
  model=SequenceModelElement.SequenceModelElement('syslog', [timeModel, FixedDataModelElement.FixedDataModelElement('sp0', ' '), hostNameModel, FixedDataModelElement.FixedDataModelElement('sp1', ' ')])
  return(model)
