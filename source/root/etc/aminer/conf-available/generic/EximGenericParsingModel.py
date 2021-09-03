"""This module defines a generic parser model for exim."""

from aminer.parsing.AnyByteDataModelElement import AnyByteDataModelElement
from aminer.parsing.DateTimeModelElement import DateTimeModelElement
from aminer.parsing.DecimalIntegerValueModelElement import DecimalIntegerValueModelElement
from aminer.parsing.DecimalFloatValueModelElement import DecimalFloatValueModelElement
from aminer.parsing.DelimitedDataModelElement import DelimitedDataModelElement
from aminer.parsing.FirstMatchModelElement import FirstMatchModelElement
from aminer.parsing.FixedDataModelElement import FixedDataModelElement
from aminer.parsing.IpAddressDataModelElement import IpAddressDataModelElement
from aminer.parsing.OptionalMatchModelElement import OptionalMatchModelElement
from aminer.parsing.SequenceModelElement import SequenceModelElement
from aminer.parsing.VariableByteDataModelElement import VariableByteDataModelElement
from aminer.parsing.RepeatedElementDataModelElement import RepeatedElementDataModelElement


def get_model():
    """Return a model to parse Exim logs from the AIT-LDS."""
    alphabet = b"!'#$%&\"()*+,-./0123456789:;<>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ\\^_`abcdefghijklmnopqrstuvwxyz{|}~=[]"

    size_str = b" SIZE="
    host_str1 = b" host "
    host_str = b":" + host_str1
    status_code421 = b": 421"
    status_code450 = b": 450 "
    status_code451 = b": 451 "
    status_code452 = b": 452 <"
    status_code550 = b": 550"
    status_code553 = b": 553 "
    status_code554 = b": 554 "
    dtme = DateTimeModelElement("time", b"%Y-%m-%d %H:%M:%S")
    msg_id = DelimitedDataModelElement("id", b" ")
    ip = IpAddressDataModelElement("ip")
    host_ip = IpAddressDataModelElement("host_ip")
    host = DelimitedDataModelElement("host", b" ")
    size = DecimalIntegerValueModelElement("size")
    port = DecimalIntegerValueModelElement("port")
    h_str = b" H="
    h_str1 = b"H="
    r_str = b" R="
    t_str = b" T="
    f_str = b" F=<"
    a_str = b" A="
    u_str = b" U="
    p_str = b" P="
    s_str = b" S="
    x_str = b" X="
    c_str = b" C=\""
    id_str = b" id="
    a = DelimitedDataModelElement("a", b" ")
    r = DelimitedDataModelElement("r", b" ")
    t = DelimitedDataModelElement("t", b" ")
    u = DelimitedDataModelElement("u", b" ")
    p = DelimitedDataModelElement("p", b" ")
    h = DelimitedDataModelElement("h", b" ")
    x = DelimitedDataModelElement("x", b" ")
    c = DelimitedDataModelElement("c", b'"')
    s = DecimalIntegerValueModelElement("s")
    mail_from = DelimitedDataModelElement("mail_from", b" ")
    smtp_error_from_remote = b"SMTP error from remote mail server after MAIL FROM:<"

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
                    ip,
                ]),
                SequenceModelElement("vrfy_failed", [
                    FixedDataModelElement("vrfy_failed_str", b"VRFY failed for "),
                    DelimitedDataModelElement("mail", b" "),
                    FixedDataModelElement("h_str", h_str),
                    h,
                    FixedDataModelElement("sp1", b" ["),
                    ip,
                    FixedDataModelElement("sp2", b"]")
                ]),
                SequenceModelElement("deferred", [
                    msg_id,
                    FixedDataModelElement("smtp_error", b" SMTP error from remote mail server after MAIL FROM:<"),
                    DelimitedDataModelElement("from_mail", b">"),
                    FixedDataModelElement("s0", b">" + size_str),
                    size,
                    FixedDataModelElement("s1", host_str),
                    host,
                    FixedDataModelElement("s2", b" ["),
                    host_ip,
                    FixedDataModelElement("status_code", b"]" + status_code421 + b" "),  # status code has always to be 421 in this error.
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
                    FixedDataModelElement("s0", h_str),
                    host,
                    FixedDataModelElement("s1", b" ["),
                    host_ip,
                    FixedDataModelElement("s2", b"]:"),
                    FixedDataModelElement("smtp_error", b" SMTP error from remote mail server after pipelined MAIL FROM:<"),
                    DelimitedDataModelElement("from_mail", b">"),
                    FixedDataModelElement("s3", b">" + size_str),
                    size,
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
                    FixedDataModelElement("smtp_error", b" SMTP error from remote mail server after end of data" + host_str),
                    host,
                    FixedDataModelElement("s0", b" ["),
                    host_ip,
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
                    FixedDataModelElement("s0", b">" + host_str),
                    host,
                    FixedDataModelElement("s1", b" ["),
                    host_ip,
                    FixedDataModelElement("status_code", b"]" + status_code450),
                    DelimitedDataModelElement("version", b" "),
                    FixedDataModelElement("msg", b" Service unavailable")
                ]),
                SequenceModelElement("host_unable_to_send", [
                    msg_id,
                    FixedDataModelElement("s0", b" == "),
                    DelimitedDataModelElement("from_mail", b" "),
                    FixedDataModelElement("s1", r_str),
                    r,
                    FixedDataModelElement("s2", t_str),
                    t,
                    FixedDataModelElement("msg", b" defer (-44): SMTP error from remote mail server after RCPT TO:<"),
                    DelimitedDataModelElement("to_mail", b">"),
                    FixedDataModelElement("s3", b">" + host_str),
                    host,
                    FixedDataModelElement("s4", b" ["),
                    host_ip,
                    FixedDataModelElement("status_code", b"]" + status_code451),
                    FixedDataModelElement("msg", b"Temporary local problem - please try later")
                ]),
                SequenceModelElement("uncomplete_sender_verify", [
                    FixedDataModelElement("s0", h_str1),
                    h,
                    FixedDataModelElement("s1", b" ("),
                    DelimitedDataModelElement("domain", b")"),
                    FixedDataModelElement("s2", b") ["),
                    IpAddressDataModelElement("ipv6", ipv6=True),
                    FixedDataModelElement("s3", b"]:"),
                    port,
                    FirstMatchModelElement("reason", [
                        SequenceModelElement("permission_denied", [
                            FixedDataModelElement("msg", b" sender verify defer for <"),
                            DelimitedDataModelElement("from_mail", b">"),
                            FixedDataModelElement("msg", b">: require_files: error for "),
                            DelimitedDataModelElement("required_file", b":"),
                            FixedDataModelElement("msg", b": Permission denied")
                        ]),
                        SequenceModelElement("rejected_rcpt", [
                            FixedDataModelElement("s0", f_str),
                            DelimitedDataModelElement("from", b">"),
                            FixedDataModelElement("s1", b">" + a_str),
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
                    FixedDataModelElement("s1", r_str),
                    r,
                    FixedDataModelElement("s2", t_str),
                    t,
                    FixedDataModelElement("msg", b" defer (-44): SMTP error from remote mail server after RCPT TO:<"),
                    DelimitedDataModelElement("mail_to", b">"),
                    FixedDataModelElement("s3", b">" + host_str),
                    host,
                    FixedDataModelElement("s4", b" ["),
                    host_ip,
                    FixedDataModelElement("status_code", b"]" + status_code452),
                    DelimitedDataModelElement("mail_to", b">"),
                    FixedDataModelElement("msg", b"> Domain size limit exceeded")
                ]),
                SequenceModelElement("verification_error", [
                    msg_id,
                    FixedDataModelElement("s0", b" ** "),
                    DelimitedDataModelElement("mail_to", b" "),
                    FixedDataModelElement("s1", r_str),
                    r,
                    FixedDataModelElement("s2", t_str),
                    DelimitedDataModelElement("t", b":"),
                    FirstMatchModelElement("fm", [
                        SequenceModelElement("verification_failed", [
                            FixedDataModelElement("msg", b": SMTP error from remote mail server after RCPT TO:<"),
                            DelimitedDataModelElement("mail_to", b">"),
                            FixedDataModelElement("s3", b">" + host_str),
                            host,
                            FixedDataModelElement("s4", b" ["),
                            host_ip,
                            FixedDataModelElement("status_code", b"]" + status_code550),
                            FixedDataModelElement("msg", b"-Verification for <"),
                            DelimitedDataModelElement("mail_from", b">"),
                            FixedDataModelElement("msg", b">\\n550-The mail server could not deliver mail to "),
                            DelimitedDataModelElement("mail_to", b" "),
                            FixedDataModelElement("msg", b" The account or domain may not exist, they may be blacklisted, or missing the"
                                                         b" proper dns entries.\\n550 Sender verify failed")
                        ]),
                        SequenceModelElement("unable_to_verify", [
                            FixedDataModelElement("msg", b": SMTP error from remote mail server after MAIL FROM:<"),
                            DelimitedDataModelElement("mail_from", b">"),
                            FixedDataModelElement("s3", b">" + size_str),
                            size,
                            FixedDataModelElement("s4", host_str),
                            host,
                            FixedDataModelElement("s5", b" ["),
                            host_ip,
                            FixedDataModelElement("status_code", b"]" + status_code553 + b"<"),
                            DelimitedDataModelElement("mail_to", b">"),
                            FixedDataModelElement("msg", b"> unable to verify address\\nVerify that SMPT authentication has been enabled.")
                        ])
                    ])
                ]),
                SequenceModelElement("mail_delivery_failure", [
                    msg_id,
                    FixedDataModelElement("s0", b" <= <>" + r_str),
                    r,
                    FixedDataModelElement("s1", u_str),
                    u,
                    FixedDataModelElement("s2", p_str),
                    p,
                    FixedDataModelElement("s3", s_str),
                    s,
                    FixedDataModelElement("s4", t_str),
                    FixedDataModelElement("t", b"\"Mail delivery failed: returning message to sender\""),
                    FixedDataModelElement("s5", b" for "),
                    VariableByteDataModelElement("mail_from", alphabet)
                ]),
                SequenceModelElement("mail_flagged_as_spam1", [
                    msg_id,
                    FixedDataModelElement("s0", h_str),
                    h,
                    FixedDataModelElement("s1", b" ["),
                    host_ip,
                    FixedDataModelElement("s2", b"]:"),
                    port,
                    FixedDataModelElement("msg", b" Warning: \"SpamAssassin as marka22 detected message as spam ("),
                    DelimitedDataModelElement("version", b")"),
                    FixedDataModelElement("s3", b")\"")
                ]),
                SequenceModelElement("mail_flagged_as_spam2", [
                    msg_id,
                    FixedDataModelElement("s0", b" <="),
                    host_ip,
                    FixedDataModelElement("s1", h_str),
                    DelimitedDataModelElement("h", b"["),
                    FixedDataModelElement("s2", b"["),
                    host_ip,
                    FixedDataModelElement("s3", b"]:"),
                    port,
                    FixedDataModelElement("s4", p_str),
                    p,
                    FixedDataModelElement("s5", s_str),
                    s,
                    FixedDataModelElement("s6", id_str),
                    msg_id,
                    FixedDataModelElement("s7", t_str),
                    AnyByteDataModelElement("msg")
                ]),
                SequenceModelElement("mail_flagged_as_spam3", [
                    msg_id,
                    FixedDataModelElement("s0", b" => "),
                    DelimitedDataModelElement("user", b" "),
                    DelimitedDataModelElement("s1", b"<", consume_delimiter=True),
                    mail_from,
                    FixedDataModelElement("s2", b" [>" + r_str),
                    r,
                    FixedDataModelElement("s3", t_str),
                    AnyByteDataModelElement("t")
                ]),
                SequenceModelElement("mail_flagged_as_spam4", [
                    msg_id,
                    FixedDataModelElement("msg", b" Completed"),
                    OptionalMatchModelElement("opt", SequenceModelElement("seq", [
                        FixedDataModelElement("s0", b" "),
                        dtme,
                        FixedDataModelElement("s1", b" "),
                        msg_id,
                        FixedDataModelElement("s2", h_str),
                        h,
                        FixedDataModelElement("s3", b" ["),
                        host_ip,
                        FixedDataModelElement("s4", b"]:"),
                        port,
                        FixedDataModelElement("msg", b" Warning: \"SpamAssassin as marka22 detected message as spam ("),
                        DelimitedDataModelElement("version", b")"),
                        FixedDataModelElement("s5", b")\"")
                    ]))
                ]),
                SequenceModelElement("mail_flagged_as_spam5", [
                    msg_id,
                    FixedDataModelElement("s0", b" <= "),
                    mail_from,
                    FixedDataModelElement("s1", h_str),
                    h,
                    FixedDataModelElement("s2", b" ["),
                    host_ip,
                    FixedDataModelElement("s3", b"]:"),
                    port,
                    FixedDataModelElement("s4", p_str),
                    p,
                    FixedDataModelElement("s5", s_str),
                    s,
                    FixedDataModelElement("s6", id_str),
                    msg_id,
                    FixedDataModelElement("s7", t_str + b'"'),
                    DelimitedDataModelElement("t", b"\""),
                    FixedDataModelElement("s8", b'" for '),
                    mail_from,
                    FixedDataModelElement("s9", b" "),
                    dtme,
                    FixedDataModelElement("s10", b" "),
                    msg_id,
                    FixedDataModelElement("s11", b" => "),
                    DelimitedDataModelElement("user", b" "),
                    FixedDataModelElement("s12", b" <"),
                    mail_from,
                    FixedDataModelElement("s13", b" [>" + r_str),
                    r,
                    FixedDataModelElement("s14", t_str),
                    AnyByteDataModelElement("t")
                ]),
                SequenceModelElement("mail_spam_allowed1", [
                    msg_id,
                    FixedDataModelElement("s0", h_str),
                    DelimitedDataModelElement("h", b"["),
                    FixedDataModelElement("s1", b"["),
                    host_ip,
                    FixedDataModelElement("s2", b"]:"),
                    port,
                    FirstMatchModelElement("fm", [
                        FixedDataModelElement("msg", b" Warning: Message has been scanned: no virus or other harmful content was found"),
                        SequenceModelElement("seq", [
                            FixedDataModelElement(
                                "msg", b" Warning: \"SpamAssassin as cpaneleximscanner detected OUTGOING smtp message as NOT spam ("),
                            DecimalFloatValueModelElement("spam_value", value_sign_type=DecimalFloatValueModelElement.SIGN_TYPE_OPTIONAL),
                            FixedDataModelElement("s3", b")\"")
                        ])
                    ])
                ]),
                SequenceModelElement("mail_spam_allowed2", [
                    msg_id,
                    FixedDataModelElement("s0", b" <= "),
                    mail_from,
                    FixedDataModelElement("s1",  h_str),
                    h,
                    FixedDataModelElement("s2", b" ["),
                    host_ip,
                    FixedDataModelElement("s3", b"]:"),
                    port,
                    FixedDataModelElement("s4", p_str),
                    p,
                    FixedDataModelElement("s5", x_str),
                    x,
                    FixedDataModelElement("s6", a_str),
                    a,
                    FixedDataModelElement("s7", s_str),
                    s,
                    FixedDataModelElement("s8", t_str),
                    t,
                    FixedDataModelElement("msg", b" plates\" for "),
                    AnyByteDataModelElement("mail_to")
                ]),
                SequenceModelElement("mail_spam_allowed3", [
                    msg_id,
                    FixedDataModelElement("msg", b" SMTP connection outbound "),
                    DecimalIntegerValueModelElement("timestamp"),
                    FixedDataModelElement("s0", b" "),
                    msg_id,
                    FixedDataModelElement("s1", b" "),
                    DelimitedDataModelElement("domain", b" "),
                    FixedDataModelElement("s2", b" "),
                    AnyByteDataModelElement("mail_to")
                ]),
                SequenceModelElement("mail_spam_allowed4", [
                    msg_id,
                    FixedDataModelElement("s0", b" => "),
                    mail_from,
                    FixedDataModelElement("s1", r_str),
                    r,
                    FixedDataModelElement("s2", t_str),
                    t,
                    FixedDataModelElement("s3", h_str),
                    h,
                    FixedDataModelElement("s4", b" ["),
                    host_ip,
                    FixedDataModelElement("s5", b"]" + x_str),
                    x,
                    FixedDataModelElement("s6", c_str),
                    c,
                    FixedDataModelElement("s7", b"\" "),
                    dtme,
                    FixedDataModelElement("s8", b" "),
                    msg_id,
                    FixedDataModelElement("s9", b" Completed"),
                ]),
                SequenceModelElement("mail_flagged_as_spam1", [
                    msg_id,
                    FixedDataModelElement("s0", h_str),
                    h,
                    FixedDataModelElement("s1", b" ["),
                    host_ip,
                    FixedDataModelElement("s2", b"]:"),
                    port,
                    FixedDataModelElement("msg", b" Warning: \"SpamAssassin as sfgthib detected message as spam ("),
                    DelimitedDataModelElement("version", b")"),
                    FixedDataModelElement("s3", b")\" "),
                    dtme,
                    FixedDataModelElement("s4", b" "),
                    msg_id,
                    FixedDataModelElement("s5", h_str),
                    h,
                    FixedDataModelElement("s6", b" ["),
                    host_ip,
                    FixedDataModelElement("s7", b"]:"),
                    port,
                    FixedDataModelElement("msg", b" Warning: Message has been scanned: no virus or other harmful content was found")
                ]),
                SequenceModelElement("mail_flagged_as_spam2", [
                    msg_id,
                    FixedDataModelElement("s0", b" <= "),
                    mail_from,
                    FixedDataModelElement("s1", h_str),
                    h,
                    FixedDataModelElement("s2", b" ["),
                    host_ip,
                    FixedDataModelElement("s3", b"]:"),
                    port,
                    FixedDataModelElement("s4", p_str),
                    p,
                    FixedDataModelElement("s5", x_str),
                    x,
                    FixedDataModelElement("s6", s_str),
                    s,
                    FixedDataModelElement("s7", id_str),
                    msg_id,
                    FixedDataModelElement("s8", t_str),
                    t,
                    FixedDataModelElement("s9", b" for "),
                    AnyByteDataModelElement("mail_to")
                ]),
                SequenceModelElement("mail", [
                    msg_id,
                    FirstMatchModelElement("dir", [
                        SequenceModelElement("dir_in", [
                            FixedDataModelElement("in", b" <= "),
                            FirstMatchModelElement("fm", [
                                SequenceModelElement("seq1", [
                                    FixedDataModelElement("brack", b"<>"),
                                    FirstMatchModelElement("fm", [
                                        SequenceModelElement("r", [
                                            FixedDataModelElement("r_str", r_str),
                                            r,
                                            FixedDataModelElement("u_str", u_str),
                                            u,
                                        ]),
                                        SequenceModelElement("h", [
                                            FixedDataModelElement("h_str", h_str),
                                            h,
                                            FixedDataModelElement("sp1", b" ["),
                                            ip,
                                            FixedDataModelElement("sp1", b"]"),
                                        ])
                                    ]),
                                    FixedDataModelElement("sp2", p_str),
                                    p,
                                    FixedDataModelElement("sp2", p_str),
                                    s,
                                ]),
                                SequenceModelElement("seq2", [
                                    DelimitedDataModelElement("mail", b" "),
                                    FixedDataModelElement("user_str", u_str),
                                    DelimitedDataModelElement("user", b" "),
                                    FixedDataModelElement("p_str", p_str),
                                    p,
                                    FixedDataModelElement("s_str", s_str),
                                    s,
                                    OptionalMatchModelElement(
                                        "id", SequenceModelElement("id", [
                                            FixedDataModelElement("id_str", id_str),
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
                            FixedDataModelElement("r_str", b">" + r_str),
                            r,
                            FixedDataModelElement("t_str", t_str),
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
            FixedDataModelElement("s1", b">" + host_str),
            host,
            FixedDataModelElement("s2", b" ["),
            host_ip,
            FixedDataModelElement("status_code", b"]" + status_code450),  # status code has to be 450 in this error message.
            DelimitedDataModelElement("version", b" "),
            FixedDataModelElement("msg", b" Client host rejected: cannot find your hostname, ["),
            host_ip,
            FixedDataModelElement("s3", b"] "),
            dtme,
            FixedDataModelElement("s4", b" "),
            msg_id,
            FixedDataModelElement("s5", b" ** "),
            DelimitedDataModelElement("to_mail", b">"),
            FixedDataModelElement("msg", b">: retry timeout exceeded")
        ]),
        SequenceModelElement("invalid_dns_record", [
            FixedDataModelElement("msg", b"SMTP error from remote mail server after RCPT TO:" + host_str),
            DelimitedDataModelElement("host", b"["),
            FixedDataModelElement("s0", b"["),
            host_ip,
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
            FixedDataModelElement("msg", b"Diagnostic-Code: X-Postfix;" + host_str1),
            host,
            FixedDataModelElement("s0", b" ["),
            host_ip,
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
            host,
            FixedDataModelElement("s0", b" ["),
            host_ip,
            FixedDataModelElement("s1", b"]:"),
            port,
            FixedDataModelElement("msg", b" is not permitted to relay 550 through this server without authentication.")
        ]),
        SequenceModelElement("bad_helo_record", [
            DelimitedDataModelElement("cipher_suite", b" "),
            FixedDataModelElement("msg", b" " + smtp_error_from_remote),
            DelimitedDataModelElement("mail_from", b">"),
            FixedDataModelElement("s0", b">" + size_str),
            size,
            FixedDataModelElement("s1", host_str),
            host,
            FixedDataModelElement("s2", b" ["),
            host_ip,
            OptionalMatchModelElement("optional", SequenceModelElement("seq", [
                FixedDataModelElement("to", b".."),
                DecimalIntegerValueModelElement("upper_ip")
            ])),
            FixedDataModelElement("status_code", b"]" + status_code550),
            FixedDataModelElement("msg", b" \"REJECTED - Bad HELO - Host impersonating ["),
            DelimitedDataModelElement("original_host", b"]"),
            FixedDataModelElement("s3", b"]\"")
        ]),
        SequenceModelElement("domain_not_exists", [
            FixedDataModelElement("msg", smtp_error_from_remote),
            DelimitedDataModelElement("mail_from", b">"),
            FixedDataModelElement("s0", b">" + host_str),
            host,
            FixedDataModelElement("s1", b" ["),
            host_ip,
            FixedDataModelElement("status_code", b"]" + status_code553),
            FixedDataModelElement("msg", b"sorry, your domain does not exists.")
        ]),
        SequenceModelElement("rejected_due_to_spam_content", [
            DateTimeModelElement("time", b"[%H:%M:%S"),
            FixedDataModelElement("hosts", b" hosts"),
            DecimalIntegerValueModelElement("hosts_number"),
            FixedDataModelElement("s0", b" "),
            RepeatedElementDataModelElement("rep", FirstMatchModelElement("fm", [
                SequenceModelElement("seq", [
                    dtme,
                    FixedDataModelElement("s1", b" "),
                    msg_id,
                    FixedDataModelElement("s2", b" <= <>" + r_str),
                    r,
                    FixedDataModelElement("s3", u_str),
                    u,
                    FixedDataModelElement("s4", p_str),
                    p,
                    FixedDataModelElement("s5", s_str),
                    s,
                    FixedDataModelElement("s6", t_str + b'"'),
                    DelimitedDataModelElement("t", b'"'),
                    FixedDataModelElement("s7", b'" for '),
                    mail_from,
                    FixedDataModelElement("s8", b" "),
                    dtme,
                    FixedDataModelElement("s9", b" cwd="),
                    DelimitedDataModelElement("cwd", b" "),
                    FixedDataModelElement("s10", b" "),
                    DecimalIntegerValueModelElement("args_num"),
                    FixedDataModelElement("s11", b" args: "),
                    RepeatedElementDataModelElement("rep", FirstMatchModelElement("fm", [
                        SequenceModelElement("seq", [
                            dtme,
                            FixedDataModelElement("s12", b" "),
                            msg_id,
                            FixedDataModelElement("s13", b" ** "),
                            mail_from,
                            FixedDataModelElement("s14", r_str),
                            r,
                            FixedDataModelElement("s15", t_str),
                            DelimitedDataModelElement("t", b":"),
                            FixedDataModelElement("msg", b": SMTP error from remote mail server after end of data" + host_str),
                            DelimitedDataModelElement("domain", b" "),
                            FixedDataModelElement("s16", b" ["),
                            host_ip,
                            FixedDataModelElement("status_code", b"]" + status_code554),
                            FixedDataModelElement("msg", b"rejected due to spam content")
                        ]),
                        # this is problematic as the number of arguments is variable!
                        SequenceModelElement("arg_seq", [
                            DelimitedDataModelElement("arg", b" "),
                            FixedDataModelElement("s17", b" ")
                        ])
                    ]))
                ]),
                # this is problematic as the number of hosts is variable!
                SequenceModelElement("host_seq", [
                    host,
                    FixedDataModelElement("s8", b" ")
                ])
            ]))
        ]),
    ])

    return model
