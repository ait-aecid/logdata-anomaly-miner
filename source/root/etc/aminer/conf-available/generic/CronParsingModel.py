from aminer.parsing import AnyByteDataModelElement
from aminer.parsing import DecimalIntegerValueModelElement
from aminer.parsing import FirstMatchModelElement
from aminer.parsing import FixedDataModelElement
from aminer.parsing import FixedWordlistDataModelElement
from aminer.parsing import OptionalMatchModelElement
from aminer.parsing import SequenceModelElement
from aminer.parsing import VariableByteDataModelElement

def getModel(userNameModel=None):
  """This function defines how to parse a cron message logged
via syslog after any standard logging preamble, e.g. from syslog."""

  if userNameModel == None:
    userNameModel=VariableByteDataModelElement.VariableByteDataModelElement('user', '0123456789abcdefghijklmnopqrstuvwxyz.-')


  typeChildren=[]
  typeChildren.append(SequenceModelElement.SequenceModelElement('exec', [
      FixedDataModelElement.FixedDataModelElement('s0', '('),
      userNameModel,
      FixedDataModelElement.FixedDataModelElement('s1', ') CMD '),
      AnyByteDataModelElement.AnyByteDataModelElement('command')
  ]))

  typeChildren.append(SequenceModelElement.SequenceModelElement('pam', [
      FixedDataModelElement.FixedDataModelElement('s0', 'pam_unix(cron:session): session '),
      FixedWordlistDataModelElement.FixedWordlistDataModelElement('change', ['opened', 'closed']),
      FixedDataModelElement.FixedDataModelElement('s1', ' for user '),
      userNameModel,
      OptionalMatchModelElement.OptionalMatchModelElement('openby', FixedDataModelElement.FixedDataModelElement('default', ' by (uid=0)')),
  ]))

  model=SequenceModelElement.SequenceModelElement('cron', [FixedDataModelElement.FixedDataModelElement('sname', 'CRON['),
      DecimalIntegerValueModelElement.DecimalIntegerValueModelElement('pid'),
      FixedDataModelElement.FixedDataModelElement('s0', ']: '),
      FirstMatchModelElement.FirstMatchModelElement('msgtype', typeChildren)])

  return(model)
