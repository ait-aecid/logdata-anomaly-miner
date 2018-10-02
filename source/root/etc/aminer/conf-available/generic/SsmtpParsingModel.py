"""This module defines a parser for ssmtp."""

from aminer.parsing import DecimalIntegerValueModelElement
from aminer.parsing import DelimitedDataModelElement
from aminer.parsing import FirstMatchModelElement
from aminer.parsing import FixedDataModelElement
from aminer.parsing import SequenceModelElement

def getModel():
  """This function returns the model."""
  typeChildren = []
  typeChildren.append(SequenceModelElement('sent', [
      FixedDataModelElement('s0', b'Sent mail for '),
      DelimitedDataModelElement('to-addr', b' ('),
      FixedDataModelElement('s1', b' ('),
      DelimitedDataModelElement('status', b') uid='),
      FixedDataModelElement('s2', b') uid='),
      DecimalIntegerValueModelElement('uid'),
      FixedDataModelElement('s3', b' username='),
      DelimitedDataModelElement('username', b' outbytes='),
      FixedDataModelElement('s4', b' outbytes='),
      DecimalIntegerValueModelElement('bytes'),
  ]))

  model = SequenceModelElement('ssmtp', [
      FixedDataModelElement('sname', b'sSMTP['),
      DecimalIntegerValueModelElement('pid'),
      FixedDataModelElement('s0', b']: '),
      FirstMatchModelElement('msg', typeChildren)])
  return model
