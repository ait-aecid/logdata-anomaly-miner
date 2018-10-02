"""This module defines a parser for cron."""

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

  if userNameModel is None:
    userNameModel = VariableByteDataModelElement('user', b'0123456789abcdefghijklmnopqrstuvwxyz.-')


  typeChildren = []
  typeChildren.append(SequenceModelElement('exec', [
      FixedDataModelElement('s0', b'('),
      userNameModel,
      FixedDataModelElement('s1', b') CMD '),
      AnyByteDataModelElement('command')
  ]))

  typeChildren.append(SequenceModelElement('pam', [
      FixedDataModelElement('s0', b'pam_unix(cron:session): session '),
      FixedWordlistDataModelElement('change', [b'opened', b'closed']),
      FixedDataModelElement('s1', b' for user '),
      userNameModel,
      OptionalMatchModelElement('openby', FixedDataModelElement('default', b' by (uid=0)')),
  ]))

  model = FirstMatchModelElement('cron', [
      SequenceModelElement('std', [
          FixedDataModelElement('sname', b'CRON['),
          DecimalIntegerValueModelElement('pid'),
          FixedDataModelElement('s0', b']: '),
          FirstMatchModelElement('msgtype', typeChildren)
      ]),
      SequenceModelElement('low', [
          FixedDataModelElement('sname', b'cron['),
          DecimalIntegerValueModelElement('pid'),
          FixedDataModelElement('s0', b']: (*system*'),
          DelimitedDataModelElement('rname', b') RELOAD ('),
          FixedDataModelElement('s1', b') RELOAD ('),
          DelimitedDataModelElement('fname', b')'),
          FixedDataModelElement('s2', b')'),
      ]),
  ])

  return model
