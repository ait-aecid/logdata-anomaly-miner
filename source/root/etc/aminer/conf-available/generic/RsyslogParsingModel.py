"""This module defines a parser for rsyslog."""

from aminer.parsing.DecimalIntegerValueModelElement import DecimalIntegerValueModelElement
from aminer.parsing.DelimitedDataModelElement import DelimitedDataModelElement
from aminer.parsing.FirstMatchModelElement import FirstMatchModelElement
from aminer.parsing.FixedDataModelElement import FixedDataModelElement
from aminer.parsing.SequenceModelElement import SequenceModelElement


def get_model():
    """Return a model to parse a su session information message after any standard logging preamble, e.g. from syslog."""
    type_children = [
        SequenceModelElement('gidchange', [
            FixedDataModelElement('s0', b'rsyslogd\'s groupid changed to '),
            DecimalIntegerValueModelElement('gid')
        ]),
        SequenceModelElement('statechange', [
            FixedDataModelElement('s0', b'[origin software="rsyslogd" swVersion="'),
            DelimitedDataModelElement('version', b'"'),
            FixedDataModelElement('s1', b'" x-pid="'),
            DecimalIntegerValueModelElement('pid'),
            FixedDataModelElement('s2', b'" x-info="http://www.rsyslog.com"] '),
            FirstMatchModelElement('type', [
                FixedDataModelElement('HUPed', b'rsyslogd was HUPed'),
                FixedDataModelElement('start', b'start')
            ])
        ]),
        SequenceModelElement('uidchange', [
            FixedDataModelElement('s0', b'rsyslogd\'s userid changed to '),
            DecimalIntegerValueModelElement('uid')
        ])
    ]

    model = SequenceModelElement('rsyslog', [
        FixedDataModelElement('sname', b'rsyslogd: '),
        FirstMatchModelElement('msg', type_children)
    ])
    return model
