"""This module defines a parser for susession."""

from aminer.parsing import DecimalIntegerValueModelElement
from aminer.parsing import DelimitedDataModelElement
from aminer.parsing import FirstMatchModelElement
from aminer.parsing import FixedDataModelElement
from aminer.parsing import FixedWordlistDataModelElement
from aminer.parsing import OptionalMatchModelElement
from aminer.parsing import SequenceModelElement
from aminer.parsing import VariableByteDataModelElement

def get_model(user_name_model=None):
  """This function defines how to parse a su session information message
after any standard logging preamble, e.g. from syslog."""

  if user_name_model is None:
    user_name_model = VariableByteDataModelElement('user', b'0123456789abcdefghijklmnopqrstuvwxyz.-')
  srcuser_name_model = VariableByteDataModelElement('srcuser', \
          b'0123456789abcdefghijklmnopqrstuvwxyz.-')

  type_children = []
  type_children.append(SequenceModelElement('su-good', [
      FixedDataModelElement('s0', b'Successful su for '),
      user_name_model,
      FixedDataModelElement('s1', b' by '),
      srcuser_name_model]))

  type_children.append(SequenceModelElement('su-good', [
      FixedDataModelElement('s0', b'+ '),
      DelimitedDataModelElement('terminal', b' '),
      FixedDataModelElement('s1', b' '),
      srcuser_name_model,
      FixedDataModelElement('s2', b':'),
      user_name_model]))

  type_children.append(SequenceModelElement('pam', [
      FixedDataModelElement('s0', b'pam_unix(su:session): session '),
      FixedWordlistDataModelElement('change', [b'opened', b'closed']),
      FixedDataModelElement('s1', b' for user '),
      user_name_model,
      OptionalMatchModelElement('openby', \
          SequenceModelElement('userinfo', [
              FixedDataModelElement('s0', b' by (uid='),
              DecimalIntegerValueModelElement('uid'),
              FixedDataModelElement('s1', b')')]))
      ]))

  model = SequenceModelElement('su', [
      FixedDataModelElement('sname', b'su['),
      DecimalIntegerValueModelElement('pid'),
      FixedDataModelElement('s0', b']: '),
      FirstMatchModelElement('msg', type_children)])
  return model
