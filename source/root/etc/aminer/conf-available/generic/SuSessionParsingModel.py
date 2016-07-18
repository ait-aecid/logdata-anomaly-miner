from aminer.parsing import DecimalIntegerValueModelElement
from aminer.parsing import FirstMatchModelElement
from aminer.parsing import FixedDataModelElement
from aminer.parsing import FixedWordlistDataModelElement
from aminer.parsing import OptionalMatchModelElement
from aminer.parsing import SequenceModelElement
from aminer.parsing import VariableByteDataModelElement

def getModel(userNameModel=None):
  """This function defines how to parse a su session information message
after any standard logging preamble, e.g. from syslog."""

  if userNameModel == None:
    userNameModel=VariableByteDataModelElement('user', '0123456789abcdefghijklmnopqrstuvwxyz.-')

  typeChildren=[]
  typeChildren.append(SequenceModelElement('pam', [
      FixedDataModelElement('s0', 'Successful su for '),
      userNameModel,
      FixedDataModelElement('s1', ' by '),
      userNameModel,
  ]))

  typeChildren.append(SequenceModelElement('pam', [
      FixedDataModelElement('s0', '+ ??? '),
      userNameModel,
      FixedDataModelElement('s1', ':'),
      userNameModel,
  ]))

  typeChildren.append(SequenceModelElement('pam', [
      FixedDataModelElement('s0', 'pam_unix(su:session): session '),
      FixedWordlistDataModelElement('change', ['opened', 'closed']),
      FixedDataModelElement('s1', ' for user '),
      userNameModel,
      OptionalMatchModelElement('openby', FixedDataModelElement('default', ' by (uid=0)')),
  ]))

  model=SequenceModelElement('su', [
      FixedDataModelElement('sname', 'su['),
      DecimalIntegerValueModelElement('pid'),
      FixedDataModelElement('s0', ']: '),
      FirstMatchModelElement('msg', typeChildren)])
  return(model)
