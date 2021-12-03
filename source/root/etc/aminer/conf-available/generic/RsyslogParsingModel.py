"""This module defines a parser for rsyslog."""

from aminer.parsing.DateTimeModelElement import DateTimeModelElement
from aminer.parsing.DecimalIntegerValueModelElement import DecimalIntegerValueModelElement
from aminer.parsing.DelimitedDataModelElement import DelimitedDataModelElement
from aminer.parsing.FirstMatchModelElement import FirstMatchModelElement
from aminer.parsing.FixedDataModelElement import FixedDataModelElement
from aminer.parsing.SequenceModelElement import SequenceModelElement
from aminer.parsing.OptionalMatchModelElement import OptionalMatchModelElement


def get_model():
    """Return a model to parse a su session information message after any standard logging preamble, e.g. from syslog."""
    type_children = [
        SequenceModelElement("gidchange", [
            FixedDataModelElement("s0", b"rsyslogd's groupid changed to "),
            DecimalIntegerValueModelElement("gid")
        ]),
        SequenceModelElement("statechange", [
            FixedDataModelElement("s0", b'[origin software="rsyslogd" swVersion="'),
            DelimitedDataModelElement("version", b'"'),
            FixedDataModelElement("s1", b'" x-pid="'),
            DecimalIntegerValueModelElement("pid"),
            FirstMatchModelElement("fm", [
                FixedDataModelElement("s2", b'" x-info="https://www.rsyslog.com"] '),
                FixedDataModelElement("s2", b'" x-info="http://www.rsyslog.com"] ')
            ]),
            FirstMatchModelElement("type", [
                FixedDataModelElement("HUPed", b"rsyslogd was HUPed"),
                FixedDataModelElement("start", b"start")
            ])
        ]),
        SequenceModelElement("uidchange", [
            FixedDataModelElement("s0", b"rsyslogd's userid changed to "),
            DecimalIntegerValueModelElement("uid")
        ]),
        SequenceModelElement("action", [
            FixedDataModelElement("s0", b"action '"),
            DelimitedDataModelElement("action", b"'"),
            FirstMatchModelElement("fm", [
                SequenceModelElement("resumed", [
                    FixedDataModelElement("s1", b"' resumed (module '"),
                    DelimitedDataModelElement("module", b"'"),
                    FixedDataModelElement("s2", b"') [try http://www.rsyslog.com/e/"),
                    DecimalIntegerValueModelElement("number"),
                    FixedDataModelElement("s3", b" ]")
                ]),
                SequenceModelElement("suspended", [
                    FixedDataModelElement("s1", b"' suspended, next retry is "),
                    DelimitedDataModelElement("dayname", b" "),
                    FixedDataModelElement("s2", b" "),
                    DateTimeModelElement("dtme", b"%b %d %H:%M:%S %Y"),
                    FixedDataModelElement("s2", b" [try http://www.rsyslog.com/e/"),
                    DecimalIntegerValueModelElement("number"),
                    FixedDataModelElement("s3", b" ]")
                ])
            ]),
        ]),
        SequenceModelElement("cmd", [
            FixedDataModelElement("s0", b"command '"),
            DelimitedDataModelElement("command", b"'"),
            FixedDataModelElement(
                "s1", b"' is currently not permitted - did you already set it via a RainerScript command (v6+ config)? ["),
            DelimitedDataModelElement("version", b"]", consume_delimiter=True)
        ])
    ]

    model = SequenceModelElement("rsyslog", [
        FixedDataModelElement("sname", b"rsyslogd"),
        OptionalMatchModelElement("opt", FirstMatchModelElement("fm", [
            DecimalIntegerValueModelElement("number"),
            SequenceModelElement("seq", [
                FixedDataModelElement("s0", b"-"),
                DecimalIntegerValueModelElement("number")
            ])
        ])),
        FixedDataModelElement("s0", b": "),
        FirstMatchModelElement("msg", type_children)
    ])
    return model
