"""This module defines a generic parser model for exim."""

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

    size = b" SIZE="
    host = b": host "
    status_code421 = b": 421"

    model = SequenceModelElement("model", [
        DateTimeModelElement("time", b"%Y-%m-%d %H:%M:%S"),
        FixedDataModelElement("sp", b" "),
        FirstMatchModelElement("fm", [
            SequenceModelElement("start", [
                FixedDataModelElement("start", b"Start queue run: pid="),
                DecimalIntegerValueModelElement("pid"),
                ]),
            SequenceModelElement("end", [
                FixedDataModelElement("end", b"End queue run: pid="),
                DecimalIntegerValueModelElement("pid"),
                ]),
            SequenceModelElement("no_host_found", [
                FixedDataModelElement("no_host_found_str", b"no host name found for IP address "),
                IpAddressDataModelElement("ip"),
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
                                ])
                            ])
                        ]),
                    SequenceModelElement("dir_out", [
                        FixedDataModelElement("in", b" => "),
                        DelimitedDataModelElement("name", b" "),
                        FixedDataModelElement("sp1", b" "),
                        OptionalMatchModelElement(
                            "mail_opt", SequenceModelElement("mail", [
                                FixedDataModelElement("brack1", b"("),
                                DelimitedDataModelElement("brack_mail", b")"),
                                FixedDataModelElement("brack2", b") "),
                                ])),
                        FixedDataModelElement("sp2", b"<"),
                        DelimitedDataModelElement("mail", b">"),
                        FixedDataModelElement("r_str", b"> R="),
                        DelimitedDataModelElement("r", b" "),
                        FixedDataModelElement("t_str", b" T="),
                        VariableByteDataModelElement("t", alphabet),
                        ]),
                    SequenceModelElement("aster", [
                        FixedDataModelElement("aster", b" ** "),
                        DelimitedDataModelElement("command", b" "),
                        FixedDataModelElement("headers_str", b' Too many "Received" headers - suspected mail loop')]),
                    FixedDataModelElement("completed", b" Completed"),
                    FixedDataModelElement("frozen", b" Message is frozen"),
                    FixedDataModelElement("frozen", b" Frozen (delivery error message)")
                ])
                ]),
            SequenceModelElement("temporary_deferred_old", [
                DelimitedDataModelElement("id", b" "),
                FixedDataModelElement("smtp_error", b" SMTP error from remote mail server after MAIL FROM:<"),
                DelimitedDataModelElement("from_mail", b">"),
                FixedDataModelElement("s0", b">" + size),
                DecimalIntegerValueModelElement("size"),
                FixedDataModelElement("s1", host),
                DelimitedDataModelElement("host", b" "),
                FixedDataModelElement("s2", b" ["),
                IpAddressDataModelElement("host_ip"),
                FixedDataModelElement("status_code", b"]: 421 "),  # status code has always to be 421 in this error message.
                DelimitedDataModelElement("version", b" "),
                FixedDataModelElement("s3", b" ["),
                DelimitedDataModelElement("domain", b"]"),
                FixedDataModelElement("s4", b"] Message from ("),
                IpAddressDataModelElement("from_ip"),
                FixedDataModelElement("s5", b") temporarily deferred - "),
                DelimitedDataModelElement("reason_code", b" "),
                FixedDataModelElement("s6", b" Please refer to "),
                VariableByteDataModelElement("refer_addr", alphabet)
            ]),
            SequenceModelElement("temporary_deferred_new", [
                DelimitedDataModelElement("id", b" "),
                FixedDataModelElement("s0", b" H="),
                DelimitedDataModelElement("host", b" "),
                FixedDataModelElement("s1", b" ["),
                IpAddressDataModelElement("host_ip"),
                FixedDataModelElement("s2", b"]:"),
                FixedDataModelElement("smtp_error", b" SMTP error from remote mail server after pipelined MAIL FROM:<"),
                DelimitedDataModelElement("from_mail", b">"),
                FixedDataModelElement("s3", b">" + size),
                DecimalIntegerValueModelElement("size"),
                FixedDataModelElement("status_code", status_code421 + b" "),  # status code has to be 421 in this error message.
                DelimitedDataModelElement("version", b" "),
                FixedDataModelElement("s4", b" ["),
                DelimitedDataModelElement("domain", b"]"),
                FixedDataModelElement("s5", b"] Messages from "),
                IpAddressDataModelElement("from_ip"),
                FixedDataModelElement("s6", b" temporarily deferred due to unexpected volume or user complaints - "),
                DelimitedDataModelElement("reason_code", b" "),
                FixedDataModelElement("s7", b" see "),
                VariableByteDataModelElement("refer_addr", alphabet)
            ]),
            SequenceModelElement("rate_limited", [
                DelimitedDataModelElement("id", b" "),
                FixedDataModelElement("smtp_error", b" SMTP error from remote mail server after end of data" + host),
                DelimitedDataModelElement("host", b" "),
                FixedDataModelElement("s0", b" ["),
                IpAddressDataModelElement("host_ip"),
                FixedDataModelElement("status_code", b"]" + status_code421 + b"-"),  # status code has to be 421 in this error message.
                DelimitedDataModelElement("version", b" "),
                FixedDataModelElement("s1", b" ["),
                IpAddressDataModelElement("ip"),
                FixedDataModelElement("s2", b" "),
                DecimalIntegerValueModelElement("number"),
                FixedDataModelElement("msg", b"] Our system has detected an unusual rate of\\n421-"),
                DelimitedDataModelElement("version", b" "),
                FixedDataModelElement("msg", b" unsolicited mail originating from your IP address. To protect our\\n421-"),
                DelimitedDataModelElement("version", b" "),
                FixedDataModelElement("msg", b" users from spam, mail sent from your IP address has been temporarily\\n421-"),
                DelimitedDataModelElement("version", b" "),
                FixedDataModelElement("msg", b" rate limited. Please visit\\n421-"),
                DelimitedDataModelElement("version", b" ", consume_delimiter=True),
                DelimitedDataModelElement("website", b" "),
                FixedDataModelElement("msg", b" to review our Bulk\\n421 "),
                DelimitedDataModelElement("version", b" "),
                FixedDataModelElement("msg", b" Email Senders Guidelines. "),
                DelimitedDataModelElement("id", b" "),
                FixedDataModelElement("gsmtp", b" - gsmtp")
            ]),

        ])
    ])

    return model
