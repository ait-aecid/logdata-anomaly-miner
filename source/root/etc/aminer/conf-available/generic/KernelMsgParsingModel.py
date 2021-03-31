"""This module defines a parser for kernelmsg."""

from aminer.parsing.AnyByteDataModelElement import AnyByteDataModelElement
from aminer.parsing.DelimitedDataModelElement import DelimitedDataModelElement
from aminer.parsing.FirstMatchModelElement import FirstMatchModelElement
from aminer.parsing.FixedDataModelElement import FixedDataModelElement
from aminer.parsing.FixedWordlistDataModelElement import FixedWordlistDataModelElement
from aminer.parsing.IpAddressDataModelElement import IpAddressDataModelElement
from aminer.parsing.SequenceModelElement import SequenceModelElement


def get_model():
    """Return a model to parse messages from kernel logging."""
    type_children = [
        SequenceModelElement('ipv4-martian', [
            FixedDataModelElement('s0', b'IPv4: martian '),
            FixedWordlistDataModelElement('direction', [b'source', b'destination']),
            FixedDataModelElement('s1', b' '),
            IpAddressDataModelElement('destination'),
            FixedDataModelElement('s2', b' from '),
            IpAddressDataModelElement('source'),
            FixedDataModelElement('s3', b', on dev '),
            AnyByteDataModelElement('interface')]),
        SequenceModelElement('net-llheader', [
            FixedDataModelElement('s0', b'll header: '),
            AnyByteDataModelElement('data')
        ]),
        AnyByteDataModelElement('unparsed')
    ]

    model = SequenceModelElement('kernel', [
        FixedDataModelElement('sname', b'kernel: ['),
        DelimitedDataModelElement('timestamp', b']'),
        FixedDataModelElement('s0', b'] '),
        FirstMatchModelElement('msg', type_children)
    ])
    return model
