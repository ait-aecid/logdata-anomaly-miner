"""This module defines a generated parser model."""

from aminer.parsing.DateTimeModelElement import DateTimeModelElement
from aminer.parsing.DecimalIntegerValueModelElement import DecimalIntegerValueModelElement
from aminer.parsing.DelimitedDataModelElement import DelimitedDataModelElement
from aminer.parsing.FirstMatchModelElement import FirstMatchModelElement
from aminer.parsing.FixedDataModelElement import FixedDataModelElement
from aminer.parsing.FixedWordlistDataModelElement import FixedWordlistDataModelElement
from aminer.parsing.IpAddressDataModelElement import IpAddressDataModelElement
from aminer.parsing.OptionalMatchModelElement import OptionalMatchModelElement
from aminer.parsing.SequenceModelElement import SequenceModelElement
from aminer.parsing.VariableByteDataModelElement import VariableByteDataModelElement


def get_model():
    """Return a model to parse Apache Access logs from the AIT-LDS."""
    alphabet = b'!"#$%&\'()*+,-./0123456789:;<>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ\\^_`abcdefghijklmnopqrstuvwxyz{|}~=[]'

    model = SequenceModelElement('model', [
        FirstMatchModelElement('client_ip', [
            IpAddressDataModelElement('client_ip'),
            FixedDataModelElement('localhost', b'::1')
            ]),
        FixedDataModelElement('sp1', b' '),
        VariableByteDataModelElement('client_id', alphabet),
        FixedDataModelElement('sp2', b' '),
        VariableByteDataModelElement('user_id', alphabet),
        FixedDataModelElement('sp3', b' ['),
        DateTimeModelElement('time', b'%d/%b/%Y:%H:%M:%S'),
        FixedDataModelElement('sp4', b' +'),
        DecimalIntegerValueModelElement('tz'),
        FixedDataModelElement('sp5', b'] "'),
        FirstMatchModelElement('fm', [
            FixedDataModelElement('dash', b'-'),
            SequenceModelElement('request', [
                FixedWordlistDataModelElement('method', [
                    b'GET', b'POST', b'PUT', b'HEAD', b'DELETE', b'CONNECT', b'OPTIONS', b'TRACE', b'PATCH']),
                FixedDataModelElement('sp6', b' '),
                DelimitedDataModelElement('request', b' ', b'\\'),
                FixedDataModelElement('sp7', b' '),
                DelimitedDataModelElement('version', b'"'),
                ])
            ]),
        FixedDataModelElement('sp8', b'" '),
        DecimalIntegerValueModelElement('status_code'),
        FixedDataModelElement('sp9', b' '),
        DecimalIntegerValueModelElement('content_size'),
        OptionalMatchModelElement(
            'combined', SequenceModelElement('combined', [
                FixedDataModelElement('sp10', b' "'),
                DelimitedDataModelElement('referer', b'"', b'\\'),
                FixedDataModelElement('sp11', b'" "'),
                DelimitedDataModelElement('user_agent', b'"', b'\\'),
                FixedDataModelElement('sp12', b'"'),
                ])),
        ])

    return model
