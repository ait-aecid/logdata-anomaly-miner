"""This module defines the parsing model for ntpd logs."""

from aminer.parsing import DecimalFloatValueModelElement
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
      'interface', b'0123456789abcdefghijklmnopqrstuvwxyz.')

  typeChildren = []
  typeChildren.append(SequenceModelElement('exit', [
      FixedDataModelElement('s0', b'ntpd exiting on signal '),
      DecimalIntegerValueModelElement('signal')
  ]))

  typeChildren.append(SequenceModelElement('listen-drop', [
      FixedDataModelElement('s0', b'Listen and drop on '),
      DecimalIntegerValueModelElement('fd'),
      FixedDataModelElement('s1', b' '),
      interfaceNameModel,
      FixedDataModelElement('s2', b' '),
      FirstMatchModelElement('address', [
          IpAddressDataModelElement('ipv4'),
          DelimitedDataModelElement('ipv6', b' '),
      ]),
      FixedDataModelElement('s3', b' UDP 123')
  ]))

  typeChildren.append(SequenceModelElement('listen-normal', [
      FixedDataModelElement('s0', b'Listen normally on '),
      DecimalIntegerValueModelElement('fd'),
      FixedDataModelElement('s1', b' '),
      interfaceNameModel,
      FixedDataModelElement('s2', b' '),
      IpAddressDataModelElement('ip'),
      FirstMatchModelElement('msg', [
          FixedDataModelElement('port-new', b':123'),
          FixedDataModelElement('port-old', b' UDP 123')
      ])
  ]))

  typeChildren.append(SequenceModelElement('listen-routing', [
      FixedDataModelElement('s0', b'Listening on routing socket on fd #'),
      DecimalIntegerValueModelElement('fd'),
      FixedDataModelElement('s1', b' for interface updates')
  ]))

  typeChildren.append(FixedDataModelElement(
      'new-interfaces', b'new interface(s) found: waking up resolver'))

  typeChildren.append(FixedDataModelElement(
      'ntp-io',
      b'ntp_io: estimated max descriptors: 1024, initial socket boundary: 16'))

  typeChildren.append(FixedDataModelElement(
      'peers-refreshed', b'peers refreshed'))

  typeChildren.append(SequenceModelElement('precision', [
      FixedDataModelElement('s0', b'proto: precision = '),
      DecimalFloatValueModelElement('precision'),
      FixedDataModelElement('s1', b' usec')
  ]))

  model = SequenceModelElement('ntpd', [
      FixedDataModelElement('sname', b'ntpd['),
      DecimalIntegerValueModelElement('pid'),
      FixedDataModelElement('s0', b']: '),
      FirstMatchModelElement('msg', typeChildren)])
  return model
