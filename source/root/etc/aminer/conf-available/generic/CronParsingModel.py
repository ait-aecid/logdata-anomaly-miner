"""This module defines a parser for cron."""

from aminer.parsing.AnyByteDataModelElement import AnyByteDataModelElement
from aminer.parsing.DecimalIntegerValueModelElement import DecimalIntegerValueModelElement
from aminer.parsing.DelimitedDataModelElement import DelimitedDataModelElement
from aminer.parsing.FirstMatchModelElement import FirstMatchModelElement
from aminer.parsing.FixedDataModelElement import FixedDataModelElement
from aminer.parsing.FixedWordlistDataModelElement import FixedWordlistDataModelElement
from aminer.parsing.OptionalMatchModelElement import OptionalMatchModelElement
from aminer.parsing.SequenceModelElement import SequenceModelElement
from aminer.parsing.VariableByteDataModelElement import VariableByteDataModelElement


def get_model(user_name_model=None):
    """Return a model to parse a cron message logged via syslog after any standard logging preamble, e.g. from syslog."""
    if user_name_model is None:
        user_name_model = VariableByteDataModelElement('user', b'0123456789abcdefghijklmnopqrstuvwxyz.-')

    type_children = [
        SequenceModelElement('exec', [
            FixedDataModelElement('s0', b'('),
            user_name_model,
            FixedDataModelElement('s1', b') CMD '),
            AnyByteDataModelElement('command')
        ]),
        SequenceModelElement('pam', [
            FixedDataModelElement('s0', b'pam_unix(cron:session): session '),
            FixedWordlistDataModelElement('change', [b'opened', b'closed']),
            FixedDataModelElement('s1', b' for user '),
            user_name_model,
            OptionalMatchModelElement('openby', FixedDataModelElement('default', b' by (uid=0)'))
        ])
    ]

    model = FirstMatchModelElement('cron', [
        SequenceModelElement('std', [
            FixedDataModelElement('sname', b'CRON['),
            DecimalIntegerValueModelElement('pid'),
            FixedDataModelElement('s0', b']: '),
            FirstMatchModelElement('msgtype', type_children)
        ]),
        SequenceModelElement('low', [
            FixedDataModelElement('sname', b'cron['),
            DecimalIntegerValueModelElement('pid'),
            FixedDataModelElement('s0', b']: (*system*'),
            DelimitedDataModelElement('rname', b') RELOAD ('),
            FixedDataModelElement('s1', b') RELOAD ('),
            DelimitedDataModelElement('fname', b')'),
            FixedDataModelElement('s2', b')'), ])
    ])
    return model
