from aminer.parsing import DecimalIntegerValueModelElement
from aminer.parsing import DelimitedDataModelElement
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
  srcUserNameModel=VariableByteDataModelElement('srcuser', '0123456789abcdefghijklmnopqrstuvwxyz.-')

  typeChildren=[]
  typeChildren.append(SequenceModelElement('su-good', [
      FixedDataModelElement('s0', 'Successful su for '),
      userNameModel,
      FixedDataModelElement('s1', ' by '),
      srcUserNameModel]))

  typeChildren.append(SequenceModelElement('su-good', [
      FixedDataModelElement('s0', '+ '),
      DelimitedDataModelElement('terminal', ' '),
      FixedDataModelElement('s1', ' '),
      srcUserNameModel,
      FixedDataModelElement('s2', ':'),
      userNameModel]))

  typeChildren.append(SequenceModelElement('pam', [
      FixedDataModelElement('s0', 'pam_unix(su:session): session '),
      FixedWordlistDataModelElement('change', ['opened', 'closed']),
      FixedDataModelElement('s1', ' for user '),
      userNameModel,
      OptionalMatchModelElement('openby',
          SequenceModelElement('userinfo', [
              FixedDataModelElement('s0', ' by (uid='),
              DecimalIntegerValueModelElement('uid'),
              FixedDataModelElement('s1', ')')]))
      ]))

  model=SequenceModelElement('su', [
      FixedDataModelElement('sname', 'su['),
      DecimalIntegerValueModelElement('pid'),
      FixedDataModelElement('s0', ']: '),
      FirstMatchModelElement('msg', typeChildren)])
  return(model)
