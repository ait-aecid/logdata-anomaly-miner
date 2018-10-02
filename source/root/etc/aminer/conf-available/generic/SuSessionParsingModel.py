"""This module defines a parser for susession."""

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

  if userNameModel is None:
    userNameModel = VariableByteDataModelElement('user', b'0123456789abcdefghijklmnopqrstuvwxyz.-')
  srcUserNameModel = VariableByteDataModelElement('srcuser', \
          b'0123456789abcdefghijklmnopqrstuvwxyz.-')

  typeChildren = []
  typeChildren.append(SequenceModelElement('su-good', [
      FixedDataModelElement('s0', b'Successful su for '),
      userNameModel,
      FixedDataModelElement('s1', b' by '),
      srcUserNameModel]))

  typeChildren.append(SequenceModelElement('su-good', [
      FixedDataModelElement('s0', b'+ '),
      DelimitedDataModelElement('terminal', b' '),
      FixedDataModelElement('s1', b' '),
      srcUserNameModel,
      FixedDataModelElement('s2', b':'),
      userNameModel]))

  typeChildren.append(SequenceModelElement('pam', [
      FixedDataModelElement('s0', b'pam_unix(su:session): session '),
      FixedWordlistDataModelElement('change', [b'opened', b'closed']),
      FixedDataModelElement('s1', b' for user '),
      userNameModel,
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
      FirstMatchModelElement('msg', typeChildren)])
  return model
