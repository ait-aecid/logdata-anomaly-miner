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

def get_model(user_name_model=None):
  """This function defines how to parse a cron message logged
via syslog after any standard logging preamble, e.g. from syslog."""

  if user_name_model is None:
    user_name_model = VariableByteDataModelElement('user', b'0123456789abcdefghijklmnopqrstuvwxyz.-')


  type_children = []
  type_children.append(SequenceModelElement('exec', [
      FixedDataModelElement('s0', b'('),
      user_name_model,
      FixedDataModelElement('s1', b') CMD '),
      AnyByteDataModelElement('command')
  ]))

  type_children.append(SequenceModelElement('pam', [
      FixedDataModelElement('s0', b'pam_unix(cron:session): session '),
      FixedWordlistDataModelElement('change', [b'opened', b'closed']),
      FixedDataModelElement('s1', b' for user '),
      user_name_model,
      OptionalMatchModelElement('openby', FixedDataModelElement('default', b' by (uid=0)')),
  ]))

  model = FirstMatchModelElement('cron', [
      SequenceModelElement('std', [
          FixedDataModelElement('sname', b'CRON['),
          DecimalIntegerValueModelElement('pid'),
          FixedDataModelElement('s0', b']: '),
          FirstMatchModelElement('msgtype', type_children)
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
