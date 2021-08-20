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
    host1 = b" host "
    host = b":" + host1
    status_code421 = b": 421"
    status_code450 = b": 450 "
    status_code451 = b": 451 "
    status_code452 = b": 452 <"
    status_code550 = b": 550"
    dtme = DateTimeModelElement("time", b"%Y-%m-%d %H:%M:%S")
    msg_id = DelimitedDataModelElement("id", b" ")
    h = b" H="
    h1 = b"H="
    r = b" R="
    t = b" T="
    f = b" F=<"
    a = b" A="
    u = b" U="
    p = b" P="
    s = b" S="

    model = FirstMatchModelElement("model", [
        SequenceModelElement("date_seq", [
            dtme,
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
                    FixedDataModelElement("h_str", h),
                    DelimitedDataModelElement("h", b" "),
                    FixedDataModelElement("sp1", b" ["),
                    IpAddressDataModelElement("ip"),
                    FixedDataModelElement("sp2", b"]")
                ]),
                SequenceModelElement("deferred", [
                    msg_id,
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
                    FirstMatchModelElement("status", [
                        SequenceModelElement("temporary", [
                            FixedDataModelElement("s4", b"] Message from ("),
                            IpAddressDataModelElement("from_ip"),
                            FixedDataModelElement("s5", b") temporarily deferred - "),
                            DelimitedDataModelElement("reason_code", b" "),
                            FixedDataModelElement("s6", b" Please refer to "),
                            VariableByteDataModelElement("refer_addr", alphabet)
                        ]),
                        SequenceModelElement("permanent", [
                            FixedDataModelElement("s4", b"] All messages from "),
                            IpAddressDataModelElement("from_ip"),
                            FixedDataModelElement("s5", b" will be permanently deferred; Retrying will NOT succeed. See "),
                            VariableByteDataModelElement("refer_addr", alphabet)
                        ])
                    ]),
                ]),
                SequenceModelElement("temporary_deferred_new", [
                    msg_id,
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
                    msg_id,
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
                    msg_id,
                    FixedDataModelElement("gsmtp", b" - gsmtp")
                ]),
                SequenceModelElement("service_unavailable", [
                    msg_id,
                    FixedDataModelElement("msg", b" SMTP error from remote mail server after RCPT TO:<"),
                    DelimitedDataModelElement("mail_to", b">"),
                    FixedDataModelElement("s0", b">" + host),
                    DelimitedDataModelElement("host", b" "),
                    FixedDataModelElement("s1", b" ["),
                    IpAddressDataModelElement("host_ip"),
                    FixedDataModelElement("status_code", b"]" + status_code450),
                    DelimitedDataModelElement("version", b" "),
                    FixedDataModelElement("msg", b" Service unavailable")
                ]),
                SequenceModelElement("host_unable_to_send", [
                    msg_id,
                    FixedDataModelElement("s0", b" == "),
                    DelimitedDataModelElement("from_mail", b" "),
                    FixedDataModelElement("s1", r),
                    DelimitedDataModelElement("r", b" "),
                    FixedDataModelElement("s2", t),
                    DelimitedDataModelElement("t", b" "),
                    FixedDataModelElement("msg", b" defer (-44): SMTP error from remote mail server after RCPT TO:<"),
                    DelimitedDataModelElement("to_mail", b">"),
                    FixedDataModelElement("s3", b">" + host),
                    DelimitedDataModelElement("host", b" "),
                    FixedDataModelElement("s4", b" ["),
                    IpAddressDataModelElement("host_ip"),
                    FixedDataModelElement("status_code", b"]" + status_code451),
                    FixedDataModelElement("msg", b"Temporary local problem - please try later")
                ]),
                SequenceModelElement("uncomplete_sender_verify", [
                    FixedDataModelElement("s0", h1),
                    DelimitedDataModelElement("h", b" "),
                    FixedDataModelElement("s1", b" ("),
                    DelimitedDataModelElement("domain", b")"),
                    FixedDataModelElement("s2", b") ["),
                    IpAddressDataModelElement("ipv6", ipv6=True),
                    FixedDataModelElement("s3", b"]:"),
                    DecimalIntegerValueModelElement("port"),
                    FirstMatchModelElement("reason", [
                        SequenceModelElement("permission_denied", [
                            FixedDataModelElement("msg", b" sender verify defer for <"),
                            DelimitedDataModelElement("from_mail", b">"),
                            FixedDataModelElement("msg", b">: require_files: error for "),
                            DelimitedDataModelElement("required_file", b":"),
                            FixedDataModelElement("msg", b": Permission denied")
                        ]),
                        SequenceModelElement("rejected_rcpt", [
                            FixedDataModelElement("s0", f),
                            DelimitedDataModelElement("from", b">"),
                            FixedDataModelElement("s1", b">" + a),
                            DelimitedDataModelElement("a", b" "),
                            FixedDataModelElement("msg", b" temporarily rejected RCPT <"),
                            DelimitedDataModelElement("rcpt", b">"),
                            FixedDataModelElement("msg", b">: Could not complete sender verify")
                        ])
                    ])
                ]),
                SequenceModelElement("domain_size_limit_exceeded", [
                    msg_id,
                    FixedDataModelElement("s0", b" =="),
                    DelimitedDataModelElement("mail_to", b" "),
                    FixedDataModelElement("s1", r),
                    DelimitedDataModelElement("r", b" "),
                    FixedDataModelElement("s2", t),
                    DelimitedDataModelElement("t", b" "),
                    FixedDataModelElement("msg", b" defer (-44): SMTP error from remote mail server after RCPT TO:<"),
                    DelimitedDataModelElement("mail_to", b">"),
                    FixedDataModelElement("s3", b">" + host),
                    DelimitedDataModelElement("host", b" "),
                    FixedDataModelElement("s4", b" ["),
                    IpAddressDataModelElement("host_ip"),
                    FixedDataModelElement("status_code", b"]" + status_code452),
                    DelimitedDataModelElement("mail_to", b">"),
                    FixedDataModelElement("msg", b"> Domain size limit exceeded")
                ]),
                SequenceModelElement("verification_failed", [
                    msg_id,
                    FixedDataModelElement("s0", b" ** "),
                    DelimitedDataModelElement("mail_to", b" "),
                    FixedDataModelElement("s1", r),
                    DelimitedDataModelElement("r", b" "),
                    FixedDataModelElement("s2", t),
                    DelimitedDataModelElement("t", b":"),
                    FixedDataModelElement("msg", b": SMTP error from remote mail server after RCPT TO:<"),
                    DelimitedDataModelElement("mail_to", b">"),
                    FixedDataModelElement("s3", b">" + host),
                    DelimitedDataModelElement("host", b" "),
                    FixedDataModelElement("s4", b" ["),
                    IpAddressDataModelElement("host_ip"),
                    FixedDataModelElement("status_code", b"]" + status_code550),
                    FixedDataModelElement("msg", b"-Verification for <"),
                    DelimitedDataModelElement("mail_from", b">"),
                    FixedDataModelElement("msg", b">\\n550-The mail server could not deliver mail to "),
                    DelimitedDataModelElement("mail_to", b" "),
                    FixedDataModelElement("msg", b" The account or domain may not exist, they may be blacklisted, or missing the proper"
                                                 b" dns entries.\\n550 Sender verify failed")
                ]),
                SequenceModelElement("mail_delivery_failure", [
                    msg_id,
                    FixedDataModelElement("s0", b" <= <>" + r),
                    DelimitedDataModelElement("r", b" "),
                    FixedDataModelElement("s1", u),
                    DelimitedDataModelElement("u", b" "),
                    FixedDataModelElement("s2", p),
                    DelimitedDataModelElement("p", b" "),
                    FixedDataModelElement("s3", s),
                    DecimalIntegerValueModelElement("s"),
                    FixedDataModelElement("s4", t),
                    FixedDataModelElement("t", b"\"Mail delivery failed: returning message to sender\""),
                    FixedDataModelElement("s5", b" for "),
                    VariableByteDataModelElement("mail_from", alphabet)
                ]),
                SequenceModelElement("mail", [
                    msg_id,
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
            ])
        ]),
        SequenceModelElement("no_date_seq", [
            FixedDataModelElement("s0", b"TO:<"),
            DelimitedDataModelElement("to_mail", b">"),
            FixedDataModelElement("s1", b">" + host),
            DelimitedDataModelElement("host", b" "),
            FixedDataModelElement("s2", b" ["),
            IpAddressDataModelElement("host_ip"),
            FixedDataModelElement("status_code", b"]" + status_code450),  # status code has to be 450 in this error message.
            DelimitedDataModelElement("version", b" "),
            FixedDataModelElement("msg", b" Client host rejected: cannot find your hostname, ["),
            IpAddressDataModelElement("host_ip"),
            FixedDataModelElement("s3", b"] "),
            dtme,
            FixedDataModelElement("s4", b" "),
            msg_id,
            FixedDataModelElement("s5", b" ** "),
            DelimitedDataModelElement("to_mail", b">"),
            FixedDataModelElement("msg", b">: retry timeout exceeded")
        ]),
        SequenceModelElement("invalid_dns_record", [
            FixedDataModelElement("msg", b"SMTP error from remote mail server after RCPT TO:" + host),
            DelimitedDataModelElement("host", b"["),
            FixedDataModelElement("s0", b"["),
            IpAddressDataModelElement("host_ip"),
            FixedDataModelElement("status_code", b"]" + status_code550),
            FixedDataModelElement("msg", b"-Sender has no A, AAAA, or MX DNS records. "),
            DelimitedDataModelElement("host", b"\\"),
            FixedDataModelElement("s1", b"\\n550 l "),
            DelimitedDataModelElement("host", b"\\"),
            FixedDataModelElement("msg", b"\\nVerify the zone file in "),
            DelimitedDataModelElement("file", b" "),
            FixedDataModelElement("msg", b" for the correct information. If it appear correct, you can run named-checkzone "
                                         b"domain.com domain.com.db to verify if named is able to load the zone.")
        ]),
        SequenceModelElement("mail_rejected", [
            FixedDataModelElement("msg", b"Diagnostic-Code: X-Postfix;" + host1),
            DelimitedDataModelElement("host", b" "),
            FixedDataModelElement("s0", b" ["),
            IpAddressDataModelElement("host_ip"),
            FixedDataModelElement("status_code", b"] said" + status_code550 + b" "),
            DelimitedDataModelElement("version", b" "),
            FixedDataModelElement("msg", b" Message rejected due to content restrictions (in reply to end of DATA command)\\nWhen you see "
                                         b"an error such as 550 "),
            VariableByteDataModelElement("version", alphabet)
        ]),
        SequenceModelElement("mail_authentication_error", [
            FixedDataModelElement("msg", b"Final-Recipient: rfc822;"),
            DelimitedDataModelElement("mail_from", b"\\"),
            FixedDataModelElement("msg", b"\\nAction: failed\\nStatus: "),
            DelimitedDataModelElement("status", b"\\"),
            FixedDataModelElement("msg", b"\\nDiagnostic-Code: smtp;550-Please turn on SMTP Authentication in your mail client.\\n550-"),
            DelimitedDataModelElement("host", b" "),
            FixedDataModelElement("s0", b" ["),
            IpAddressDataModelElement("host_ip"),
            FixedDataModelElement("s1", b"]:"),
            DecimalIntegerValueModelElement("port"),
            FixedDataModelElement("msg", b" is not permitted to relay 550 through this server without authentication.")
        ]),
        SequenceModelElement("bad_helo_record", [
            DelimitedDataModelElement("cipher_suite", b" "),
            FixedDataModelElement("msg", b" SMTP error from remote mail server after MAIL FROM:<"),
            DelimitedDataModelElement("mail_from", b">"),
            FixedDataModelElement("s0", b">" + size),
            DecimalIntegerValueModelElement("size"),
            FixedDataModelElement("s1", host),
            DelimitedDataModelElement("host", b" "),
            FixedDataModelElement("s2", b" ["),
            IpAddressDataModelElement("host_ip"),
            OptionalMatchModelElement("optional", SequenceModelElement("seq", [
                FixedDataModelElement("to", b".."),
                DecimalIntegerValueModelElement("upper_ip")
            ])),
            FixedDataModelElement("status_code", b"]" + status_code550),
            FixedDataModelElement("msg", b" \"REJECTED - Bad HELO - Host impersonating ["),
            DelimitedDataModelElement("original_host", b"]"),
            FixedDataModelElement("s3", b"]\"")
        ]),
    ])

    return model
