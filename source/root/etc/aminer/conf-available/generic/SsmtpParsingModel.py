"""This module defines a parser for ssmtp."""

from aminer.parsing.DecimalIntegerValueModelElement import DecimalIntegerValueModelElement
from aminer.parsing.DelimitedDataModelElement import DelimitedDataModelElement
from aminer.parsing.FirstMatchModelElement import FirstMatchModelElement
from aminer.parsing.FixedDataModelElement import FixedDataModelElement
from aminer.parsing.SequenceModelElement import SequenceModelElement


def get_model():
    """Return the model."""
    type_children = [
        SequenceModelElement('sent', [
            FixedDataModelElement('s0', b'Sent mail for '),
            DelimitedDataModelElement('to-addr', b' ('),
            FixedDataModelElement('s1', b' ('),
            DelimitedDataModelElement('status', b') uid='),
            FixedDataModelElement('s2', b') uid='),
            DecimalIntegerValueModelElement('uid'),
            FixedDataModelElement('s3', b' username='),
            DelimitedDataModelElement('username', b' outbytes='),
            FixedDataModelElement('s4', b' outbytes='),
            DecimalIntegerValueModelElement('bytes')
        ])
    ]

    model = SequenceModelElement('ssmtp', [
        FixedDataModelElement('sname', b'sSMTP['),
        DecimalIntegerValueModelElement('pid'),
        FixedDataModelElement('s0', b']: '),
        FirstMatchModelElement('msg', type_children)
    ])
    return model
