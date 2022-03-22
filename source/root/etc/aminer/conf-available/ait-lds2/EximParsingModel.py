"""This module defines a parser model for exim."""

from aminer.parsing.AnyByteDataModelElement import AnyByteDataModelElement
from aminer.parsing.DateTimeModelElement import DateTimeModelElement
from aminer.parsing.DecimalIntegerValueModelElement import DecimalIntegerValueModelElement
from aminer.parsing.DelimitedDataModelElement import DelimitedDataModelElement
from aminer.parsing.FirstMatchModelElement import FirstMatchModelElement
from aminer.parsing.FixedDataModelElement import FixedDataModelElement
from aminer.parsing.IpAddressDataModelElement import IpAddressDataModelElement
from aminer.parsing.OptionalMatchModelElement import OptionalMatchModelElement
from aminer.parsing.SequenceModelElement import SequenceModelElement
from aminer.parsing.VariableByteDataModelElement import VariableByteDataModelElement


def get_model():
    """Return a model to parse Exim logs from the AIT-LDS."""
    alphabet = b"!'#$%&\"()*+,-./0123456789:;<>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ\\^_`abcdefghijklmnopqrstuvwxyz{|}~=[]"

    model = SequenceModelElement("model", [
        DateTimeModelElement("time", b"%Y-%m-%d %H:%M:%S"),
        FixedDataModelElement("sp", b" "),
        FirstMatchModelElement("fm", [
            SequenceModelElement("start", [
                FixedDataModelElement("start", b"Start queue run: pid="),
                DecimalIntegerValueModelElement("pid"),
                ]),
            SequenceModelElement("start", [
                FixedDataModelElement("start", b"TLS error"),
                AnyByteDataModelElement('remainder')
                ]),
            SequenceModelElement("end", [
                FixedDataModelElement("end", b"End queue run: pid="),
                DecimalIntegerValueModelElement("pid"),
                ]),
            SequenceModelElement("no_host_found", [
                FixedDataModelElement("no_host_found_str", b"no host name found for IP address "),
                IpAddressDataModelElement("ip"),
                ]),
            SequenceModelElement("start_daemon", [
                FixedDataModelElement("start_daemon_str", b"exim "),
                DelimitedDataModelElement("version", b" "),
                FixedDataModelElement("start_deamon_str2", b" daemon started"),
                AnyByteDataModelElement("msg")
                ]),
            SequenceModelElement("vrfy_failed", [
                FixedDataModelElement("vrfy_failed_str", b"VRFY failed for "),
                DelimitedDataModelElement("mail", b" "),
                FixedDataModelElement("h_str", b" H="),
                DelimitedDataModelElement("h", b" "),
                FixedDataModelElement("sp1", b" ["),
                IpAddressDataModelElement("ip"),
                FixedDataModelElement("sp2", b"]")
                ]),
            SequenceModelElement("mail", [
                DelimitedDataModelElement("id", b" "),
                FirstMatchModelElement("dir", [
                    SequenceModelElement("dir_in", [
                        FixedDataModelElement("in", b" <= "),
                        FirstMatchModelElement("fm", [
                            SequenceModelElement("seq1", [
                                FixedDataModelElement("brack", b"<> "),
                                FirstMatchModelElement("fm", [
                                    SequenceModelElement("r", [
                                        FixedDataModelElement("r_str", b"R="),
                                        DelimitedDataModelElement("r", b" "),
                                        FixedDataModelElement("u_str", b" U="),
                                        DelimitedDataModelElement("u", b" "),
                                        ]),
                                    SequenceModelElement("h", [
                                        FixedDataModelElement("h_str", b"H="),
                                        DelimitedDataModelElement("h", b" "),
                                        FixedDataModelElement("sp1", b" ["),
                                        IpAddressDataModelElement("ip"),
                                        FixedDataModelElement("sp1", b"]"),
                                        ])
                                    ]),
                                FixedDataModelElement("sp2", b" P="),
                                DelimitedDataModelElement("p", b" "),
                                FixedDataModelElement("sp2", b" S="),
                                DecimalIntegerValueModelElement("s"),
                                ]),
                            SequenceModelElement("seq2", [
                                DelimitedDataModelElement("mail", b" "),
                                FixedDataModelElement("user_str", b" U="),
                                DelimitedDataModelElement("user", b" "),
                                FixedDataModelElement("p_str", b" P="),
                                DelimitedDataModelElement("p", b" "),
                                FixedDataModelElement("s_str", b" S="),
                                DecimalIntegerValueModelElement("s"),
                                OptionalMatchModelElement(
                                    "id", SequenceModelElement("id", [
                                        FixedDataModelElement("id_str", b" id="),
                                        AnyByteDataModelElement("id")
                                        ])
                                    )
                                ]),
                            AnyByteDataModelElement('remainder')
                            ])
                        ]),
                    SequenceModelElement("dir_out", [
                        FixedDataModelElement("in", b" => "),
                        DelimitedDataModelElement("name", b" "),
                        FirstMatchModelElement('fm', [
                            SequenceModelElement('seq', [
                                FixedDataModelElement("sp1", b" "),
                                OptionalMatchModelElement(
                                    "mail_opt",
                                    SequenceModelElement(
                                        "mail", [
                                            FixedDataModelElement("brack1", b"("),
                                            DelimitedDataModelElement("brack_mail", b")"),
                                            FixedDataModelElement("brack2", b") "),
                                        ])
                                ),
                                OptionalMatchModelElement(
                                    "opt",
                                    SequenceModelElement(
                                        "seq", [
                                            FixedDataModelElement("sp2", b"<"),
                                            DelimitedDataModelElement("mail", b">"),
                                            FixedDataModelElement("closing_brack", b"> "),
                                        ])
                                ),
                                FixedDataModelElement("r_str", b"R="),
                                DelimitedDataModelElement("r", b" "),
                                FixedDataModelElement("t_str", b" T="),
                                VariableByteDataModelElement("t", alphabet),
                                OptionalMatchModelElement(
                                    "param_opt",
                                    SequenceModelElement(
                                        "seq", [
                                            FixedDataModelElement("h_str", b" H="),
                                            DelimitedDataModelElement("h", b" X="),
                                            FixedDataModelElement("x_str", b" X="),
                                            DelimitedDataModelElement("x", b" CV="),
                                            FixedDataModelElement("cv_str", b" CV="),
                                            DelimitedDataModelElement("cv", b" DN="),
                                            FixedDataModelElement("dn_str", b" DN="),
                                            DelimitedDataModelElement("dn", b" C="),
                                            AnyByteDataModelElement("c"),
                                        ]))
                                ]),
                            ])
                        ]),
                    SequenceModelElement("aster", [
                        FixedDataModelElement("aster", b" ** "),
                        DelimitedDataModelElement("command", b" "),
                        FixedDataModelElement("headers_str", b' Too many "Received" headers - suspected mail loop')]),
                    SequenceModelElement("prdr", [
                        FixedDataModelElement("prdr", b" PRDR "),
                        AnyByteDataModelElement('remainder')]),
                    SequenceModelElement("arrw", [
                        FixedDataModelElement("arrw", b" -> "),
                        AnyByteDataModelElement('remainder')]),
                    FixedDataModelElement("completed", b" Completed"),
                    FixedDataModelElement("frozen", b" Message is frozen"),
                    FixedDataModelElement("frozen", b" Frozen (delivery error message)")
                ])
                ])])])

    return model
