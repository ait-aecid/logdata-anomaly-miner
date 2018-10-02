"""This module defines a parser for kernelmsg."""

from aminer.parsing import AnyByteDataModelElement
from aminer.parsing import DelimitedDataModelElement
from aminer.parsing import FirstMatchModelElement
from aminer.parsing import FixedDataModelElement
from aminer.parsing import FixedWordlistDataModelElement
from aminer.parsing import IpAddressDataModelElement
from aminer.parsing import SequenceModelElement

def getModel():
  """This function defines how to parse messages from kernel logging."""

  typeChildren = []
  typeChildren.append(SequenceModelElement('ipv4-martian', [
      FixedDataModelElement('s0', b'IPv4: martian '),
      FixedWordlistDataModelElement('direction', [b'source', b'destination']),
      FixedDataModelElement('s1', b' '),
      IpAddressDataModelElement('destination'),
      FixedDataModelElement('s2', b' from '),
      IpAddressDataModelElement('source'),
      FixedDataModelElement('s3', b', on dev '),
      AnyByteDataModelElement('interface')
  ]))

  typeChildren.append(SequenceModelElement('net-llheader', [
      FixedDataModelElement('s0', b'll header: '),
      AnyByteDataModelElement('data')]))

  typeChildren.append(AnyByteDataModelElement('unparsed'))

  model = SequenceModelElement('kernel', [
      FixedDataModelElement('sname', b'kernel: ['),
      DelimitedDataModelElement('timestamp', b']'),
      FixedDataModelElement('s0', b'] '),
      FirstMatchModelElement('msg', typeChildren)])
  return model
