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
      FixedDataModelElement('s0', 'IPv4: martian '),
      FixedWordlistDataModelElement('direction', ['source', 'destination']),
      FixedDataModelElement('s1', ' '),
      IpAddressDataModelElement('destination'),
      FixedDataModelElement('s2', ' from '),
      IpAddressDataModelElement('source'),
      FixedDataModelElement('s3', ', on dev '),
      AnyByteDataModelElement('interface')
  ]))

  typeChildren.append(SequenceModelElement('net-llheader', [
      FixedDataModelElement('s0', 'll header: '),
      AnyByteDataModelElement('data')]))

  typeChildren.append(AnyByteDataModelElement('unparsed'))

  model=SequenceModelElement('kernel', [
      FixedDataModelElement('sname', 'kernel: ['),
      DelimitedDataModelElement('timestamp', ']'),
      FixedDataModelElement('s0', '] '),
      FirstMatchModelElement('msg', typeChildren)])
  return(model)
