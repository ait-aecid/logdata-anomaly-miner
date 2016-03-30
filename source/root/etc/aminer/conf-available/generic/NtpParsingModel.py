from aminer.parsing import DecimalIntegerValueModelElement
from aminer.parsing import DelimitedDataModelElement
from aminer.parsing import FirstMatchModelElement
from aminer.parsing import FixedDataModelElement
from aminer.parsing import IpAddressDataModelElement
from aminer.parsing import OptionalMatchModelElement
from aminer.parsing import SequenceModelElement
from aminer.parsing import VariableByteDataModelElement

def getModel():
  interfaceNameModel=VariableByteDataModelElement.VariableByteDataModelElement('interface', '0123456789abcdefghijklmnopqrstuvwxyz.')

  typeChildren=[]
  typeChildren.append(SequenceModelElement.SequenceModelElement('exit', [
      FixedDataModelElement.FixedDataModelElement('s0', 'ntpd exiting on signal '),
      DecimalIntegerValueModelElement.DecimalIntegerValueModelElement('signal')
  ]))

  typeChildren.append(SequenceModelElement.SequenceModelElement('listen-drop', [
      FixedDataModelElement.FixedDataModelElement('s0', 'Listen and drop on '),
      DecimalIntegerValueModelElement.DecimalIntegerValueModelElement('fd'),
      FixedDataModelElement.FixedDataModelElement('s1', ' '),
      interfaceNameModel,
      FixedDataModelElement.FixedDataModelElement('s2', ' '),
      FirstMatchModelElement.FirstMatchModelElement('address', [
          IpAddressDataModelElement.IpAddressDataModelElement('ipv4'),
          DelimitedDataModelElement.DelimitedDataModelElement('ipv6', ' '),
      ]),
      FixedDataModelElement.FixedDataModelElement('s3', ' UDP 123')
  ]))

  typeChildren.append(SequenceModelElement.SequenceModelElement('listen-normal', [
      FixedDataModelElement.FixedDataModelElement('s0', 'Listen normally on '),
      DecimalIntegerValueModelElement.DecimalIntegerValueModelElement('fd'),
      FixedDataModelElement.FixedDataModelElement('s1', ' '),
      interfaceNameModel,
      FixedDataModelElement.FixedDataModelElement('s2', ' '),
      IpAddressDataModelElement.IpAddressDataModelElement('ip'),
      FixedDataModelElement.FixedDataModelElement('s3', ' UDP 123')
  ]))

  typeChildren.append(SequenceModelElement.SequenceModelElement('listen-routing', [
      FixedDataModelElement.FixedDataModelElement('s0', 'Listening on routing socket on fd #'),
      DecimalIntegerValueModelElement.DecimalIntegerValueModelElement('fd'),
      FixedDataModelElement.FixedDataModelElement('s1', ' for interface updates')
  ]))

  typeChildren.append(FixedDataModelElement.FixedDataModelElement('ntp-io', 'ntp_io: estimated max descriptors: 1024, initial socket boundary: 16'))

  typeChildren.append(FixedDataModelElement.FixedDataModelElement('peers-refreshed', 'peers refreshed'))

  typeChildren.append(SequenceModelElement.SequenceModelElement('precision', [
      FixedDataModelElement.FixedDataModelElement('s0', 'proto: precision = '),
      DelimitedDataModelElement.DelimitedDataModelElement('precision', ' '),
      FixedDataModelElement.FixedDataModelElement('s1', ' usec')
  ]))

  model=SequenceModelElement.SequenceModelElement('ntpd', [FixedDataModelElement.FixedDataModelElement('sname', 'ntpd['),
      DecimalIntegerValueModelElement.DecimalIntegerValueModelElement('pid'),
      FixedDataModelElement.FixedDataModelElement('s0', ']: '),
      FirstMatchModelElement.FirstMatchModelElement('msg', typeChildren)])
  return(model)
