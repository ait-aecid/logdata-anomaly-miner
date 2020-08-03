"""This module defines a generated parser model."""

from aminer.parsing import DateTimeModelElement
from aminer.parsing import DecimalFloatValueModelElement
from aminer.parsing import DecimalIntegerValueModelElement
from aminer.parsing import DelimitedDataModelElement
from aminer.parsing import FirstMatchModelElement
from aminer.parsing import FixedDataModelElement
from aminer.parsing import IpAddressDataModelElement
from aminer.parsing import OptionalMatchModelElement
from aminer.parsing import SequenceModelElement
from aminer.parsing import VariableByteDataModelElement

def getModel():

    """This model defines how to parse Apache Access logs from the AIT-LDS."""

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
        DelimitedDataModelElement('request', b'"', b'\\'),
        FixedDataModelElement('sp6', b'" '),
        DecimalIntegerValueModelElement('status_code'),
        FixedDataModelElement('sp7', b' '),
        DecimalIntegerValueModelElement('content_size'),
        OptionalMatchModelElement('combined',
            SequenceModelElement('combined', [
                FixedDataModelElement('sp8', b' "'),
                DelimitedDataModelElement('referer', b'"', b'\\'),
                FixedDataModelElement('sp9', b'" "'),
                DelimitedDataModelElement('user_agent', b'"', b'\\'),
                FixedDataModelElement('sp10', b'"'),
                ])),
        ])

    return model
