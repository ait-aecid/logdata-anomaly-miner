from aminer.parsing import AnyByteDataModelElement
from aminer.parsing import DecimalIntegerValueModelElement
from aminer.parsing import DelimitedDataModelElement
from aminer.parsing import FirstMatchModelElement
from aminer.parsing import FixedDataModelElement
from aminer.parsing import SequenceModelElement
from aminer.parsing import VariableByteDataModelElement

def getSystemdModel():
  typeChildren=[]
  typeChildren.append(AnyByteDataModelElement('unparsed'))

  model=SequenceModelElement('systemd', [
      FixedDataModelElement('sname', 'systemd['),
      DecimalIntegerValueModelElement('pid'),
      FixedDataModelElement('s0', ']: '),
      FirstMatchModelElement('msg', typeChildren)])
  return(model)


def getLogindModel(userNameModel=None):
  """This function defines how to parse a systemd logind daemon
  message after any standard logging preamble, e.g. from syslog."""

  if userNameModel == None:
    userNameModel=VariableByteDataModelElement('user', '0123456789abcdefghijklmnopqrstuvwxyz-')

  typeChildren=[]
# FIXME: Will fail on username models including the dot at the end.
  typeChildren.append(SequenceModelElement('new session', [
      FixedDataModelElement('s0', 'New session '),
      DecimalIntegerValueModelElement('session'),
      FixedDataModelElement('s1', ' of user '),
      userNameModel,
      FixedDataModelElement('s2', '.')]))

  typeChildren.append(SequenceModelElement('removed session', [
      FixedDataModelElement('s0', 'Removed session '),
      DecimalIntegerValueModelElement('session'),
      FixedDataModelElement('s1', '.')]))

  model=SequenceModelElement('systemd-logind', [
      FixedDataModelElement('sname', 'systemd-logind['),
      DecimalIntegerValueModelElement('pid'),
      FixedDataModelElement('s0', ']: '),
      FirstMatchModelElement('msg', typeChildren)])
  return(model)


def getTmpfilesModel():
  """This function defines how to parse a systemd tmpfiles daemon
  message after any standard logging preamble, e.g. from syslog."""

  typeChildren=[]
# FIXME: Will fail on username models including the dot at the end.
  typeChildren.append(SequenceModelElement('duplicate', [
      FixedDataModelElement('s0', '[/usr/lib/tmpfiles.d/var.conf:14] Duplicate line for path "'),
      DelimitedDataModelElement('path', '", ignoring.'),
      FixedDataModelElement('s2', '", ignoring.')]))

  model=SequenceModelElement('systemd-tmpfiles', [
      FixedDataModelElement('sname', 'systemd-tmpfiles['),
      DecimalIntegerValueModelElement('pid'),
      FixedDataModelElement('s0', ']: '),
      FirstMatchModelElement('msg', typeChildren)])
  return(model)
