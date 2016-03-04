from aminer.parsing import DecimalIntegerValueModelElement
from aminer.parsing import FirstMatchModelElement
from aminer.parsing import FixedDataModelElement
from aminer.parsing import SequenceModelElement
from aminer.parsing import VariableByteDataModelElement

from aminer.parsing import DebugModelElement

def getLogindModel(userNameModel=None):
  """This function defines how to parse a systemd logind daemon
  message after any standard logging preamble, e.g. from syslog."""

  if userNameModel == None:
    userNameModel=VariableByteDataModelElement.VariableByteDataModelElement('user', '0123456789abcdefghijklmnopqrstuvwxyz-')

  typeChildren=[]
# FIXME: Will fail on username models including the dot at the en.d
  typeChildren.append(SequenceModelElement.SequenceModelElement('new session', [
      FixedDataModelElement.FixedDataModelElement('s0', 'New session '),
      DecimalIntegerValueModelElement.DecimalIntegerValueModelElement('session'),
      FixedDataModelElement.FixedDataModelElement('s1', ' of user '),
      userNameModel,
      FixedDataModelElement.FixedDataModelElement('s2', '.')]))

  typeChildren.append(SequenceModelElement.SequenceModelElement('removed session', [
      FixedDataModelElement.FixedDataModelElement('s0', 'Removed session '),
      DecimalIntegerValueModelElement.DecimalIntegerValueModelElement('session'),
      FixedDataModelElement.FixedDataModelElement('s1', '.')]))

  model=SequenceModelElement.SequenceModelElement('systemd-logind', [
      FixedDataModelElement.FixedDataModelElement('sname', 'systemd-logind['),
      DecimalIntegerValueModelElement.DecimalIntegerValueModelElement('pid'),
      FixedDataModelElement.FixedDataModelElement('s0', ']: '),
      FirstMatchModelElement.FirstMatchModelElement('msg', typeChildren)])
  return(model)
