"""This module defines a generated parser model."""

from aminer.parsing.AnyByteDataModelElement import AnyByteDataModelElement
from aminer.parsing.DateTimeModelElement import DateTimeModelElement
from aminer.parsing.DecimalIntegerValueModelElement import DecimalIntegerValueModelElement
from aminer.parsing.DelimitedDataModelElement import DelimitedDataModelElement
from aminer.parsing.FirstMatchModelElement import FirstMatchModelElement
from aminer.parsing.FixedDataModelElement import FixedDataModelElement
from aminer.parsing.FixedWordlistDataModelElement import FixedWordlistDataModelElement
from aminer.parsing.IpAddressDataModelElement import IpAddressDataModelElement
from aminer.parsing.SequenceModelElement import SequenceModelElement
from aminer.parsing.OptionalMatchModelElement import OptionalMatchModelElement


def get_model():
    """Return a model to parse Apache Error logs from the AIT-LDS."""
    model = FirstMatchModelElement("model", [
        FixedDataModelElement("mkdir_failed", b"mkdir failed on directory /var/run/samba/msg.lock: Permission denied"),
        SequenceModelElement("with_data", [
            FixedDataModelElement("sp1", b"["),
            FixedWordlistDataModelElement("day", [b"Mon", b"Tue", b"Wed", b"Thu", b"Fri", b"Sat", b"Sun"]),
            FixedDataModelElement("sp2", b" "),
            DateTimeModelElement("time", b"%b %d %H:%M:%S.%f %Y"),
            FixedDataModelElement("bracket_str", b"] ["),
            DelimitedDataModelElement("source", b"]"),
            FixedDataModelElement("pid_str", b"] [pid "),
            DecimalIntegerValueModelElement("pid"),
            FixedDataModelElement("bracket_str", b"] "),
            FirstMatchModelElement("fm", [
                SequenceModelElement("client", [
                    FixedDataModelElement("client_str", b"[client "),
                    IpAddressDataModelElement("client_ip"),
                    FixedDataModelElement("colon", b":"),
                    DecimalIntegerValueModelElement("client_port"),
                    FirstMatchModelElement("fm", [
                        SequenceModelElement("php", [
                            FixedDataModelElement("php", b"] PHP "),
                            FirstMatchModelElement("fphp", [
                                SequenceModelElement("warning", [
                                    FixedDataModelElement("warning_str", b"Warning:  "),
                                    FirstMatchModelElement("warning", [
                                        SequenceModelElement("declaration", [
                                            FixedDataModelElement("declaration_str", b"Declaration of "),
                                            DelimitedDataModelElement("function", b")"),
                                            FixedDataModelElement("compatible_str", b") should be compatible with "),
                                            DelimitedDataModelElement("function2", b")"),
                                            FixedDataModelElement("compatible_str", b") in "),
                                            DelimitedDataModelElement("path", b" "),
                                            FixedDataModelElement("compatible_str", b" on line "),
                                            DecimalIntegerValueModelElement("line"),
                                            FixedDataModelElement("referer_str", b", referer: "),
                                            AnyByteDataModelElement("referer")]),
                                        SequenceModelElement("system", [
                                            FixedDataModelElement("system_str", b"system(): Cannot execute a blank command in "),
                                            DelimitedDataModelElement("path", b" "),
                                            FixedDataModelElement("compatible_str", b" on line "),
                                            DecimalIntegerValueModelElement("line")]),
                                        AnyByteDataModelElement("warning_msg")
                                        ])]),
                                SequenceModelElement("notice", [
                                    FixedDataModelElement("notice_str", b"Notice:  Undefined index: "),
                                    DelimitedDataModelElement("command", b" "),
                                    FixedDataModelElement("sp", b" in "),
                                    DelimitedDataModelElement("path", b" "),
                                    FixedDataModelElement("compatible_str", b" on line "),
                                    DecimalIntegerValueModelElement("line")]),
                                SequenceModelElement("deprecated", [
                                    FixedDataModelElement("deprecated_str", b"Deprecated:  Methods with the same name as their class "
                                                                            b"will not be constructors in a future version of PHP; "),
                                    DelimitedDataModelElement("class", b" "),
                                    FixedDataModelElement("constructor_str", b" has a deprecated constructor in "),
                                    DelimitedDataModelElement("path", b" "),
                                    FixedDataModelElement("compatible_str", b" on line "),
                                    DecimalIntegerValueModelElement("line"),
                                    FixedDataModelElement("referer_str", b", referer: "),
                                    AnyByteDataModelElement("referer"),
                                ]),
                                SequenceModelElement("fatal", [
                                    FixedDataModelElement("fatal_str", b"Fatal error:  "),
                                    AnyByteDataModelElement("error_msg")
                                    ])
                                ])
                        ]),
                        SequenceModelElement("ah", [
                            FixedDataModelElement("ah_str", b"] AH"),
                            DecimalIntegerValueModelElement("ah_number", value_pad_type=DecimalIntegerValueModelElement.PAD_TYPE_ZERO),
                            FixedDataModelElement("colon", b": "),
                            AnyByteDataModelElement("msg")
                            ]),
                        SequenceModelElement("script", [
                            FixedDataModelElement("script_str", b"] script '"),
                            DelimitedDataModelElement("script_path", b"'"),
                            FixedDataModelElement("msg", b"' not found or unable to stat"),
                            OptionalMatchModelElement("referer", SequenceModelElement("referer", [
                                FixedDataModelElement("referer_str", b", referer: "),
                                AnyByteDataModelElement("referer")
                                ]))
                            ])
                        ]),
                    ]),
                SequenceModelElement("notice", [
                    FixedDataModelElement("ah_str", b"AH"),
                    DecimalIntegerValueModelElement("ah_number", value_pad_type=DecimalIntegerValueModelElement.PAD_TYPE_ZERO),
                    FixedDataModelElement("colon", b": "),
                    AnyByteDataModelElement("msg")
                ]),
                SequenceModelElement("end_of_file", [
                    FixedDataModelElement("end_of_file_str", b"(70014)End of file found: [client "),
                    IpAddressDataModelElement("client_ip"),
                    FixedDataModelElement("colon", b":"),
                    DecimalIntegerValueModelElement("port"),
                    FixedDataModelElement("error_msg", b"] AH01102: error reading status line from remote server "),
                    DelimitedDataModelElement("domain", b":"),
                    FixedDataModelElement("colon", b":"),
                    DecimalIntegerValueModelElement("remote_port")
                ])
            ])
        ])])
    return model
