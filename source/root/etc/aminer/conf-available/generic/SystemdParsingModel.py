"""This module contains functions and classes to create the parsing model."""

from aminer.parsing.DecimalFloatValueModelElement import DecimalFloatValueModelElement
from aminer.parsing.DecimalIntegerValueModelElement import DecimalIntegerValueModelElement
from aminer.parsing.DelimitedDataModelElement import DelimitedDataModelElement
from aminer.parsing.FirstMatchModelElement import FirstMatchModelElement
from aminer.parsing.FixedDataModelElement import FixedDataModelElement
from aminer.parsing.OptionalMatchModelElement import OptionalMatchModelElement
from aminer.parsing.SequenceModelElement import SequenceModelElement
from aminer.parsing.VariableByteDataModelElement import VariableByteDataModelElement


def get_systemd_model():
    """Return the parsing model for messages directly from systemd."""
    type_children = [
        FixedDataModelElement('apt-daily-start', b'Starting Daily apt activities...'),
        FixedDataModelElement('apt-daily-started', b'Started Daily apt activities.'),
        SequenceModelElement('apt-daily-timer', [
            FixedDataModelElement('s0', b'apt-daily.timer: Adding '),
            OptionalMatchModelElement('hopt', SequenceModelElement('hblock', [
                DecimalIntegerValueModelElement('hours'),
                FixedDataModelElement('s1', b'h ')
            ])),
            DecimalIntegerValueModelElement('minutes'),
            FixedDataModelElement('s2', b'min '),
            DecimalFloatValueModelElement('seconds'),
            FixedDataModelElement('s3', b's random time.')
        ]),
        FixedDataModelElement('tmp-file-cleanup', b'Starting Cleanup of Temporary Directories...'),
        FixedDataModelElement('tmp-file-cleanup-started', b'Started Cleanup of Temporary Directories.')
    ]

    model = SequenceModelElement('systemd', [
        FixedDataModelElement('sname', b'systemd['),
        DecimalIntegerValueModelElement('pid'),
        FixedDataModelElement('s0', b']: '),
        FirstMatchModelElement('msg', type_children)
    ])
    return model


def get_logind_model(user_name_model=None):
    """Return a model to parse a systemd logind daemon message after any standard logging preamble, e.g. from syslog."""
    if user_name_model is None:
        user_name_model = VariableByteDataModelElement('user', b'0123456789abcdefghijklmnopqrstuvwxyz-')

    type_children = [
        SequenceModelElement('new session', [
            FixedDataModelElement('s0', b'New session '),
            DecimalIntegerValueModelElement('session'),
            FixedDataModelElement('s1', b' of user '),
            user_name_model,
            FixedDataModelElement('s2', b'.')
        ]),
        SequenceModelElement('removed session', [
            FixedDataModelElement('s0', b'Removed session '),
            DecimalIntegerValueModelElement('session'),
            FixedDataModelElement('s1', b'.')
        ])
    ]
    # Will fail on username models including the dot at the end.

    model = SequenceModelElement('systemd-logind', [
        FixedDataModelElement('sname', b'systemd-logind['),
        DecimalIntegerValueModelElement('pid'),
        FixedDataModelElement('s0', b']: '),
        FirstMatchModelElement('msg', type_children)
    ])
    return model


def get_tmp_files_model():
    """Return a model to parse a systemd tmpfiles daemon message after any standard logging preamble, e.g. from syslog."""
    type_children = [
        SequenceModelElement('duplicate', [
            FixedDataModelElement('s0', b'[/usr/lib/tmpfiles.d/var.conf:14] Duplicate line for path "'),
            DelimitedDataModelElement('path', b'", ignoring.'),
            FixedDataModelElement('s2', b'", ignoring.')
        ])
    ]
    # Will fail on username models including the dot at the end.

    model = SequenceModelElement('systemd-tmpfiles', [
        FixedDataModelElement('sname', b'systemd-tmpfiles['),
        DecimalIntegerValueModelElement('pid'),
        FixedDataModelElement('s0', b']: '),
        FirstMatchModelElement('msg', type_children)
    ])
    return model
