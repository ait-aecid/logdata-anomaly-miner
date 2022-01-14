"""This module contains functions and classes to create the parsing model."""

from aminer.parsing.DecimalFloatValueModelElement import DecimalFloatValueModelElement
from aminer.parsing.DecimalIntegerValueModelElement import DecimalIntegerValueModelElement
from aminer.parsing.DelimitedDataModelElement import DelimitedDataModelElement
from aminer.parsing.FirstMatchModelElement import FirstMatchModelElement
from aminer.parsing.FixedDataModelElement import FixedDataModelElement
from aminer.parsing.OptionalMatchModelElement import OptionalMatchModelElement
from aminer.parsing.SequenceModelElement import SequenceModelElement
from aminer.parsing.VariableByteDataModelElement import VariableByteDataModelElement


def get_model():
    """Return the model of all three types."""
    model = FirstMatchModelElement("systemd-fm", [
        get_systemd_model(),
        get_logind_model(),
        get_tmp_files_model()
    ])
    return model


def get_systemd_model():
    """Return the parsing model for messages directly from systemd."""
    type_children = [
        FixedDataModelElement("apt-daily-start", b"Starting Daily apt upgrade and clean activities..."),
        FixedDataModelElement("apt-daily-started", b"Started Daily apt upgrade and clean activities."),
        FixedDataModelElement("apt-daily-finished", b"Finished Daily apt upgrade and clean activities."),
        SequenceModelElement("service-succeeded", [
            DelimitedDataModelElement("service", b" "),
            FixedDataModelElement("s0", b" Succeeded.")
        ]),
        FixedDataModelElement("clean-php", b"Finished Clean php session files."),
        FixedDataModelElement("finished-logrotate", b"Finished Rotate log files."),
        FixedDataModelElement("finished-man-db-daily", b"Finished Daily man-db regeneration."),
        FixedDataModelElement("finished-ubuntu-advantages", b"Finished Ubuntu Advantage APT and MOTD Messages."),
        FixedDataModelElement("finished-refresh", b"Finished Refresh fwupd metadata and update motd."),
        FixedDataModelElement("finished-daily-apt", b"Finished Daily apt download activities."),
        SequenceModelElement("apt-daily-timer", [
            FixedDataModelElement("s0", b"apt-daily.timer: Adding "),
            OptionalMatchModelElement("hopt", SequenceModelElement("hblock", [
                DecimalIntegerValueModelElement("hours"),
                FixedDataModelElement("s1", b"h ")
            ])),
            DecimalIntegerValueModelElement("minutes"),
            FixedDataModelElement("s2", b"min "),
            DecimalFloatValueModelElement("seconds"),
            FixedDataModelElement("s3", b"s random time.")
        ]),
        FixedDataModelElement("tmp-file-cleanup", b"Starting Cleanup of Temporary Directories..."),
        FixedDataModelElement("tmp-file-cleanup-started", b"Started Cleanup of Temporary Directories."),
        SequenceModelElement("killing-process", [
            DelimitedDataModelElement("service", b":"),
            FixedDataModelElement("s0", b": Killing process "),
            DecimalIntegerValueModelElement("pid"),
            FixedDataModelElement("s1", b" (update-notifier) with signal SIGKILL.")
        ]),
        SequenceModelElement("starting", [
            FixedDataModelElement("s0", b"Starting "),
            DelimitedDataModelElement("service", b"."),
            FixedDataModelElement("s1", b"...")
        ]),
        SequenceModelElement("started", [
            FixedDataModelElement("s0", b"Started "),
            DelimitedDataModelElement("service", b".", consume_delimiter=True)
        ]),
        FixedDataModelElement("reloading", b"Reloading.")
    ]

    model = SequenceModelElement("systemd", [
        FixedDataModelElement("sname", b"systemd["),
        DecimalIntegerValueModelElement("pid"),
        FixedDataModelElement("s0", b"]: "),
        FirstMatchModelElement("msg", type_children)
    ])
    return model


def get_logind_model(user_name_model=None):
    """Return a model to parse a systemd logind daemon message after any standard logging preamble, e.g. from syslog."""
    if user_name_model is None:
        user_name_model = VariableByteDataModelElement("user", b"0123456789abcdefghijklmnopqrstuvwxyz-_")

    type_children = [
        SequenceModelElement("new session", [
            FixedDataModelElement("s0", b"New session "),
            DecimalIntegerValueModelElement("session"),
            FixedDataModelElement("s1", b" of user "),
            user_name_model,
            FixedDataModelElement("s2", b".")
        ]),
        SequenceModelElement("removed session", [
            FixedDataModelElement("s0", b"Removed session "),
            DecimalIntegerValueModelElement("session"),
            FixedDataModelElement("s1", b".")
        ]),
        SequenceModelElement("logged out", [
            FixedDataModelElement("s0", b"Session "),
            DecimalIntegerValueModelElement("session"),
            FixedDataModelElement("s1", b" logged out. Waiting for processes to exit.")
        ]),
        FixedDataModelElement("failed abandon", b"Failed to abandon session scope: Transport endpoint is not connected")
    ]
    # Will fail on username models including the dot at the end.

    model = SequenceModelElement("systemd-logind", [
        FixedDataModelElement("sname", b"systemd-logind["),
        DecimalIntegerValueModelElement("pid"),
        FixedDataModelElement("s0", b"]: "),
        FirstMatchModelElement("msg", type_children)
    ])
    return model


def get_tmp_files_model():
    """Return a model to parse a systemd tmpfiles daemon message after any standard logging preamble, e.g. from syslog."""
    type_children = [
        SequenceModelElement("duplicate", [
            FixedDataModelElement("s0", b'[/usr/lib/tmpfiles.d/var.conf:14] Duplicate line for path "'),
            DelimitedDataModelElement("path", b'", ignoring.'),
            FixedDataModelElement("s2", b'", ignoring.')
        ])
    ]
    # Will fail on username models including the dot at the end.

    model = SequenceModelElement("systemd-tmpfiles", [
        FixedDataModelElement("sname", b"systemd-tmpfiles["),
        DecimalIntegerValueModelElement("pid"),
        FixedDataModelElement("s0", b"]: "),
        FirstMatchModelElement("msg", type_children)
    ])
    return model
