import DateTimeModelElement
import FixedDataModelElement
import SequenceModelElement
import VariableByteDataModelElement

"""This class defines the model for parsing a standard syslog
preamble including timestamp and hostname."""
def getModel():
  timeModel=DateTimeModelElement.DateTimeModelElement('time', '%b %d %H:%M:%S', 15, False)
  hostNameModel=VariableByteDataModelElement.VariableByteDataModelElement('host', '-.01234567890abcdefghijklmnopqrstuvwxyz')
  model=SequenceModelElement.SequenceModelElement('syslog', [timeModel, FixedDataModelElement.FixedDataModelElement('sp0', ' '), hostNameModel, FixedDataModelElement.FixedDataModelElement('sp1', ' ')])
  return(model)
