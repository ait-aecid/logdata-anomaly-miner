"""This module defines the parsing model for ntpd logs."""

from aminer.parsing import DecimalFloatValueModelElemen
from aminer.parsing import DecimalIntegerValueModelElement
from aminer.parsing import DelimitedDataModelElement
from aminer.parsing import FirstMatchModelElement
from aminer.parsing import FixedDataModelElement
from aminer.parsing import IpAddressDataModelElement
from aminer.parsing import SequenceModelElement
from aminer.parsing import VariableByteDataModelElement

def getModel():
  """Get the model."""
  interfaceNameModel = VariableByteDataModelElement(
      'interface', '0123456789abcdefghijklmnopqrstuvwxyz.')

  typeChildren = []
  typeChildren.append(SequenceModelElement('exit', [
      FixedDataModelElement('s0', 'ntpd exiting on signal '),
      DecimalIntegerValueModelElement('signal')
  ]))

  typeChildren.append(SequenceModelElement('listen-drop', [
      FixedDataModelElement('s0', 'Listen and drop on '),
      DecimalIntegerValueModelElement('fd'),
      FixedDataModelElement('s1', ' '),
      interfaceNameModel,
      FixedDataModelElement('s2', ' '),
      FirstMatchModelElement('address', [
          IpAddressDataModelElement('ipv4'),
          DelimitedDataModelElement('ipv6', ' '),
      ]),
      FixedDataModelElement('s3', ' UDP 123')
  ]))

  typeChildren.append(SequenceModelElement('listen-normal', [
      FixedDataModelElement('s0', 'Listen normally on '),
      DecimalIntegerValueModelElement('fd'),
      FixedDataModelElement('s1', ' '),
      interfaceNameModel,
      FixedDataModelElement('s2', ' '),
      IpAddressDataModelElement('ip'),
      FirstMatchModelElement('msg', [
          FixedDataModelElement('port-new', ':123'),
          FixedDataModelElement('port-old', ' UDP 123')
      ])
  ]))

  typeChildren.append(SequenceModelElement('listen-routing', [
      FixedDataModelElement('s0', 'Listening on routing socket on fd #'),
      DecimalIntegerValueModelElement('fd'),
      FixedDataModelElement('s1', ' for interface updates')
  ]))

  typeChildren.append(FixedDataModelElement(
      'new-interfaces', 'new interface(s) found: waking up resolver'))

  typeChildren.append(FixedDataModelElement(
      'ntp-io',
      'ntp_io: estimated max descriptors: 1024, initial socket boundary: 16'))

  typeChildren.append(FixedDataModelElement(
      'peers-refreshed', 'peers refreshed'))

  typeChildren.append(SequenceModelElement('precision', [
      FixedDataModelElement('s0', 'proto: precision = '),
      DecimalFloatValueModelElemen('precision'),
      FixedDataModelElement('s1', ' usec')
  ]))

  model = SequenceModelElement('ntpd', [
      FixedDataModelElement('sname', 'ntpd['),
      DecimalIntegerValueModelElement('pid'),
      FixedDataModelElement('s0', ']: '),
      FirstMatchModelElement('msg', typeChildren)])
  return model
