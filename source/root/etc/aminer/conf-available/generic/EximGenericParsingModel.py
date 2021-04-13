"""This module defines a parser model for exim."""

from aminer.parsing.AnyByteDataModelElement import AnyByteDataModelElement
from aminer.parsing.DecimalIntegerValueModelElement import DecimalIntegerValueModelElement
from aminer.parsing.DelimitedDataModelElement import DelimitedDataModelElement
from aminer.parsing.FirstMatchModelElement import FirstMatchModelElement
from aminer.parsing.FixedDataModelElement import FixedDataModelElement
from aminer.parsing.FixedWordlistDataModelElement import FixedWordlistDataModelElement
from aminer.parsing.IpAddressDataModelElement import IpAddressDataModelElement
from aminer.parsing.OptionalMatchModelElement import OptionalMatchModelElement
from aminer.parsing.SequenceModelElement import SequenceModelElement
from aminer.parsing.WhiteSpaceLimitedDataModelElement import WhiteSpaceLimitedDataModelElement


def get_model():
    """Return a model to parse a su session information message after any standard logging preamble, e.g. from syslog."""
    type_children = [
        SequenceModelElement('queue', [
            FixedWordlistDataModelElement('type', [b'Start', b'End']),
            FixedDataModelElement('s0', b' queue run: pid='),
            DecimalIntegerValueModelElement('pid')
        ]),
        SequenceModelElement('rec-log', [
            WhiteSpaceLimitedDataModelElement('id'),
            FixedDataModelElement('s0', b' <= '),
            WhiteSpaceLimitedDataModelElement('env-from'),
            FirstMatchModelElement('source', [
                SequenceModelElement('network', [
                    FixedDataModelElement('s0', b' H=('),
                    DelimitedDataModelElement('hostname', b') '),
                    FixedDataModelElement('s1', b') ['),
                    IpAddressDataModelElement('hostip'),
                    FixedDataModelElement('s2', b']')
                ]),
                SequenceModelElement('user', [
                    FixedDataModelElement('s0', b' U='),
                    WhiteSpaceLimitedDataModelElement('user')
                ])
            ]),
            FixedDataModelElement('s2', b' P='),
            WhiteSpaceLimitedDataModelElement('proto'),
            FixedDataModelElement('s3', b' S='),
            DecimalIntegerValueModelElement('size'),
            OptionalMatchModelElement('idopt', SequenceModelElement('iddata', [
                FixedDataModelElement('s0', b' id='),
                AnyByteDataModelElement('id')
            ]))
        ]),
        SequenceModelElement('send-log', [
            WhiteSpaceLimitedDataModelElement('id'),
            # Strange: first address seems to use different separator than second one.
            FixedWordlistDataModelElement('s0', [b' => b', b' ->']),
            DelimitedDataModelElement('env-to', b' R='),
            FixedDataModelElement('s1', b' R='),
            WhiteSpaceLimitedDataModelElement('route'),
            FixedDataModelElement('s2', b' T='),
            WhiteSpaceLimitedDataModelElement('transport'),
            AnyByteDataModelElement('unparsed')
        ]),
        SequenceModelElement('sent', [
            WhiteSpaceLimitedDataModelElement('id'),
            FixedDataModelElement('s0', b' Completed')
        ]),
        SequenceModelElement('started', [
            FixedDataModelElement('s0', b' exim '),
            WhiteSpaceLimitedDataModelElement('version'),
            FixedDataModelElement('s1', b' daemon started: pid='),
            DecimalIntegerValueModelElement('pid'),
            FixedDataModelElement('s2', b', -q30m, listening for SMTP on [127.0.0.1]:25')
        ])
    ]

    model = SequenceModelElement('exim', [
        FixedDataModelElement('sname', b'exim['),
        DecimalIntegerValueModelElement('pid'),
        FixedDataModelElement('s0', b']: '),
        FirstMatchModelElement('msg', type_children)
    ])
    return model
