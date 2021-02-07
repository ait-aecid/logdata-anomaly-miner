"""This module defines the parsing model for ntpd logs."""

from aminer.parsing.DecimalFloatValueModelElement import DecimalFloatValueModelElement
from aminer.parsing.DecimalIntegerValueModelElement import DecimalIntegerValueModelElement
from aminer.parsing.DelimitedDataModelElement import DelimitedDataModelElement
from aminer.parsing.FirstMatchModelElement import FirstMatchModelElement
from aminer.parsing.FixedDataModelElement import FixedDataModelElement
from aminer.parsing.IpAddressDataModelElement import IpAddressDataModelElement
from aminer.parsing.SequenceModelElement import SequenceModelElement
from aminer.parsing.VariableByteDataModelElement import VariableByteDataModelElement


def get_model():
    """Get the model."""
    interface_name_model = VariableByteDataModelElement('interface', b'0123456789abcdefghijklmnopqrstuvwxyz.')

    type_children = [
        SequenceModelElement('exit', [
            FixedDataModelElement('s0', b'ntpd exiting on signal '),
            DecimalIntegerValueModelElement('signal')
        ]),
        SequenceModelElement('listen-drop', [
            FixedDataModelElement('s0', b'Listen and drop on '),
            DecimalIntegerValueModelElement('fd'),
            FixedDataModelElement('s1', b' '),
            interface_name_model,
            FixedDataModelElement('s2', b' '),
            FirstMatchModelElement('address', [
                IpAddressDataModelElement('ipv4'),
                DelimitedDataModelElement('ipv6', b' ')
            ]),
            FixedDataModelElement('s3', b' UDP 123')
        ]),
        SequenceModelElement('listen-normal', [
            FixedDataModelElement('s0', b'Listen normally on '),
            DecimalIntegerValueModelElement('fd'),
            FixedDataModelElement('s1', b' '),
            interface_name_model,
            FixedDataModelElement('s2', b' '),
            IpAddressDataModelElement('ip'),
            FirstMatchModelElement('msg', [
                FixedDataModelElement('port-new', b':123'),
                FixedDataModelElement('port-old', b' UDP 123')
            ])
        ]),
        SequenceModelElement('listen-routing', [
            FixedDataModelElement('s0', b'Listening on routing socket on fd #'),
            DecimalIntegerValueModelElement('fd'),
            FixedDataModelElement('s1', b' for interface updates')
        ]),
        FixedDataModelElement('new-interfaces', b'new interface(s) found: waking up resolver'),
        FixedDataModelElement('ntp-io', b'ntp_io: estimated max descriptors: 1024, initial socket boundary: 16'),
        FixedDataModelElement('peers-refreshed', b'peers refreshed'),
        SequenceModelElement('precision', [
            FixedDataModelElement('s0', b'proto: precision = '),
            DecimalFloatValueModelElement('precision'),
            FixedDataModelElement('s1', b' usec')])]

    model = SequenceModelElement('ntpd', [
        FixedDataModelElement('sname', b'ntpd['),
        DecimalIntegerValueModelElement('pid'),
        FixedDataModelElement('s0', b']: '),
        FirstMatchModelElement('msg', type_children)
    ])
    return model
