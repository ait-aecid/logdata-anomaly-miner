from aminer.parsing import AnyByteDataModelElement
from aminer.parsing import DecimalIntegerValueModelElement
from aminer.parsing import DelimitedDataModelElement
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
    userNameModel=VariableByteDataModelElement('user', '0123456789abcdefghijklmnopqrstuvwxyz.-')


  typeChildren=[]
  typeChildren.append(SequenceModelElement('exec', [
      FixedDataModelElement('s0', '('),
      userNameModel,
      FixedDataModelElement('s1', ') CMD '),
      AnyByteDataModelElement('command')
  ]))

  typeChildren.append(SequenceModelElement('pam', [
      FixedDataModelElement('s0', 'pam_unix(cron:session): session '),
      FixedWordlistDataModelElement('change', ['opened', 'closed']),
      FixedDataModelElement('s1', ' for user '),
      userNameModel,
      OptionalMatchModelElement('openby', FixedDataModelElement('default', ' by (uid=0)')),
  ]))

  model=FirstMatchModelElement('cron', [
      SequenceModelElement('std', [
          FixedDataModelElement('sname', 'CRON['),
          DecimalIntegerValueModelElement('pid'),
          FixedDataModelElement('s0', ']: '),
          FirstMatchModelElement('msgtype', typeChildren)
      ]),
      SequenceModelElement('low', [
          FixedDataModelElement('sname', 'cron['),
          DecimalIntegerValueModelElement('pid'),
          FixedDataModelElement('s0', ']: (*system*'),
          DelimitedDataModelElement('rname', ') RELOAD ('),
          FixedDataModelElement('s1', ') RELOAD ('),
          DelimitedDataModelElement('fname', ')'),
          FixedDataModelElement('s2', ')'),
      ]),
  ])

  return(model)
