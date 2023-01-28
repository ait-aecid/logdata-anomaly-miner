"""This module defines a generated parser model."""

from aminer.parsing.AnyByteDataModelElement import AnyByteDataModelElement
from aminer.parsing.DateTimeModelElement import DateTimeModelElement
from aminer.parsing.DecimalIntegerValueModelElement import DecimalIntegerValueModelElement
from aminer.parsing.DelimitedDataModelElement import DelimitedDataModelElement
from aminer.parsing.FirstMatchModelElement import FirstMatchModelElement
from aminer.parsing.FixedDataModelElement import FixedDataModelElement
from aminer.parsing.FixedWordlistDataModelElement import FixedWordlistDataModelElement
from aminer.parsing.IpAddressDataModelElement import IpAddressDataModelElement
from aminer.parsing.OptionalMatchModelElement import OptionalMatchModelElement
from aminer.parsing.SequenceModelElement import SequenceModelElement
from aminer.parsing.VariableByteDataModelElement import VariableByteDataModelElement


def get_model():
    """Return a model to parse Syslogs from the AIT-LDS."""
    alphabet = b"!'#$%&\"()*+,-./0123456789:;<>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ\\^_`abcdefghijklmnopqrstuvwxyz{|}~=[]"

    user_info = SequenceModelElement("user_info", [
        FixedDataModelElement("user_str", b"user=<"),
        OptionalMatchModelElement(
            "user", DelimitedDataModelElement("user", b">")
            ),
        FixedDataModelElement("method_str", b">"),
        OptionalMatchModelElement(
            "method", SequenceModelElement("method", [
                FixedDataModelElement("method_str", b", method="),
                DelimitedDataModelElement("method", b","),
                ])
            ),
        FixedDataModelElement("rip_str", b", rip="),
        IpAddressDataModelElement("rip"),
        FixedDataModelElement("lip_str", b", lip="),
        IpAddressDataModelElement("lip"),
        OptionalMatchModelElement(
            "mpid", SequenceModelElement("mpid", [
                FixedDataModelElement("mpid_str", b", mpid="),
                DecimalIntegerValueModelElement("mpid"),
                ])
            ),
        OptionalMatchModelElement(
            "secured", FixedDataModelElement("secured_str", b", secured")
            ),
        OptionalMatchModelElement(
            "tls", FixedDataModelElement("tls_str", b", TLS")
            ),
        OptionalMatchModelElement(
            "handshaking", SequenceModelElement("seq", [
                FixedDataModelElement("handshaking_str", b" handshaking:"),
                DelimitedDataModelElement("msg", b", session=<")
                ])
            ),
        FixedDataModelElement("session_str", b", session=<"),
        DelimitedDataModelElement("session", b">"),
        FixedDataModelElement("bracket_str", b">"),
        ])

    model = SequenceModelElement("model", [
        DateTimeModelElement("time", b"%b %d %H:%M:%S", start_year=2022),
        FixedDataModelElement("sp1", b" "),
        DelimitedDataModelElement("host", b" "),
        FirstMatchModelElement("service", [
            SequenceModelElement("dovecot", [
                FixedDataModelElement("dovecot_str", b" dovecot: "),
                FirstMatchModelElement("imap", [
                    SequenceModelElement("imap", [
                        FixedDataModelElement("imap_str", b"imap("),
                        DelimitedDataModelElement("user", b")"),
                        FixedDataModelElement("bracket_str", b"): "),
                        FirstMatchModelElement("message", [
                            SequenceModelElement("logout", [
                                FixedDataModelElement("logout_str", b"Logged out in="),
                                DecimalIntegerValueModelElement("in"),
                                FixedDataModelElement("out_str", b" out="),
                                DecimalIntegerValueModelElement("out")
                                ]),
                            SequenceModelElement("err_mail", [
                                FixedDataModelElement("mail_str", b"Error: Failed to autocreate mailbox INBOX: Internal error occurred. "
                                                      b"Refer to server log for more information. ["),
                                DelimitedDataModelElement("err_time", b"]"),
                                FixedDataModelElement("brack", b"]")
                                ]),
                            SequenceModelElement("err_open", [
                                FixedDataModelElement("err_str", b"Error: "),
                                DelimitedDataModelElement("function_name", b"("),
                                FixedDataModelElement("brack_str1", b"("),
                                DelimitedDataModelElement("arg", b")"),
                                FixedDataModelElement("failed_str", b") failed: Permission denied (euid="),
                                DecimalIntegerValueModelElement("euid"),
                                FixedDataModelElement("brack_str2", b"("),
                                DelimitedDataModelElement("euid_user", b")"),
                                FixedDataModelElement("egid_str", b") egid="),
                                DecimalIntegerValueModelElement("egid"),
                                FixedDataModelElement("brack_str3", b"("),
                                DelimitedDataModelElement("egid_user", b")"),
                                FixedDataModelElement("perm_str", b") missing +w perm: "),
                                DelimitedDataModelElement("mail_path", b","),
                                FixedDataModelElement("group_str", b", we're not in group "),
                                DecimalIntegerValueModelElement("group_id"),
                                FixedDataModelElement("brack_str4", b"("),
                                DelimitedDataModelElement("group_name", b")"),
                                FixedDataModelElement("owned_str", b"), dir owned by "),
                                DelimitedDataModelElement("owner", b" "),
                                FixedDataModelElement("mode_str", b" mode="),
                                DelimitedDataModelElement("mode", b")"),
                                FixedDataModelElement("brack_str5", b")"),
                                OptionalMatchModelElement(
                                    "set", SequenceModelElement("set", [
                                        FixedDataModelElement("set_str", b" (set"),
                                        DelimitedDataModelElement("param", b"="),
                                        FixedDataModelElement("equal_str", b"="),
                                        DelimitedDataModelElement("val", b")"),
                                        FixedDataModelElement("brack_str6", b")")
                                        ])
                                    )
                                ]),
                            SequenceModelElement("err_mail", [
                                FixedDataModelElement("mail_str", b"Failed to autocreate mailbox INBOX: Internal error occurred. "
                                                      b"Refer to server log for more information. ["),
                                DelimitedDataModelElement("err_time", b"]"),
                                FixedDataModelElement("brack", b"]")
                                ]),
                            ]),
                        ]),
                    SequenceModelElement("imap_login", [
                        FixedDataModelElement("imap_login_str", b"imap-login: "),
                        FirstMatchModelElement("login", [
                            SequenceModelElement("disconnected_str", [
                                FixedDataModelElement("disconnected_str", b"Disconnected "),
                                FirstMatchModelElement("auth", [
                                    SequenceModelElement("auth_failed", [
                                        FixedDataModelElement("auth_failed_str", b"(auth failed, "),
                                        DecimalIntegerValueModelElement("attempts"),
                                        FixedDataModelElement("attempts_str", b" attempts in "),
                                        ]),
                                    FixedDataModelElement("no_auth_str", b"(no auth attempts in "),
                                    FixedDataModelElement("no_auth_str", b"(disconnected before auth was ready, waited "),
                                    ]),
                                DecimalIntegerValueModelElement("duration"),
                                FixedDataModelElement("secs_str", b" secs): "),
                                user_info
                                ]),
                            SequenceModelElement("login", [
                                FixedDataModelElement("login_str", b"Login: "),
                                user_info
                                ]),
                            SequenceModelElement("anvil", [
                                FixedDataModelElement("anvil_str", b"Error: anvil:"),
                                AnyByteDataModelElement("anvil_msg")
                                ]),
                            SequenceModelElement("auth_responding", [
                                FixedDataModelElement("auth_responding_str", b"Warning: Auth process not responding, "
                                                      b"delayed sending initial response (greeting): "),
                                user_info
                                ]),
                            ]),
                        ]),
                    SequenceModelElement("auth", [
                        FixedDataModelElement("auth_worker_str", b"auth: "),
                        AnyByteDataModelElement("message")
                        ]),
                    SequenceModelElement("auth_worker", [
                        FixedDataModelElement("auth_worker_str", b"auth-worker("),
                        DecimalIntegerValueModelElement("pid"),
                        FixedDataModelElement("brack", b"):"),
                        AnyByteDataModelElement("message")
                        ]),
                    SequenceModelElement("master", [
                        FixedDataModelElement("master_str", b"master: "),
                        AnyByteDataModelElement("message")
                        ])
                    ]),
                ]),
            SequenceModelElement("horde", [
                FixedDataModelElement("horde_str", b" HORDE: "),
                FirstMatchModelElement("horde", [
                    SequenceModelElement("imp", [
                        FixedDataModelElement("succ_str", b"[imp] "),
                        FirstMatchModelElement("imp", [
                            SequenceModelElement("login", [
                                FixedDataModelElement("succ_str", b"Login success for "),
                                DelimitedDataModelElement("user", b" "),
                                FixedDataModelElement("brack_str1", b" ("),
                                DelimitedDataModelElement("ip", b")"),
                                OptionalMatchModelElement(
                                    "fwd",
                                    SequenceModelElement(
                                        "seq", [
                                            FixedDataModelElement("brack_str2", b") ("),
                                            DelimitedDataModelElement("forward", b")"),
                                        ])
                                ),
                                FixedDataModelElement("to_str", b") to {"),
                                DelimitedDataModelElement("imap_addr", b"}"),
                                FixedDataModelElement("brack_str3", b"}"),
                                ]),
                            SequenceModelElement("message_sent", [
                                FixedDataModelElement("message_sent_str", b"Message sent to "),
                                DelimitedDataModelElement('recepients', b' from'),
                                FixedDataModelElement("from_str", b" from "),
                                DelimitedDataModelElement("user", b" "),
                                FixedDataModelElement("brack_str1", b" ("),
                                IpAddressDataModelElement("ip"),
                                FixedDataModelElement("brack_str2", b")"),
                                ]),
                            SequenceModelElement("login_failed", [
                                FixedDataModelElement("succ_str", b"FAILED LOGIN for "),
                                DelimitedDataModelElement("user", b" "),
                                FixedDataModelElement("brack_str1", b" ("),
                                IpAddressDataModelElement("ip"),
                                FixedDataModelElement("to_str", b") to {"),
                                DelimitedDataModelElement("imap_addr", b"}"),
                                FixedDataModelElement("brack_str2", b"}"),
                                ]),
                            SequenceModelElement("status", [
                                FixedDataModelElement("status_str", b'[status] Could not open mailbox "INBOX".'),
                                ]),
                            SequenceModelElement("sync_token", [
                                FixedDataModelElement("sync_token_str", b"[getSyncToken] IMAP error reported by server."),
                                ]),
                            SequenceModelElement("auth_failed", [
                                FixedDataModelElement("auth_failed_str", b"[login] Authentication failed."),
                                ]),
                            ]),
                        ]),
                    SequenceModelElement("horde", [
                        FixedDataModelElement("succ_str", b"[horde] "),
                        FirstMatchModelElement("horde", [
                            SequenceModelElement("success", [
                                FixedDataModelElement("success_str", b"Login success for "),
                                DelimitedDataModelElement("user", b" "),
                                FixedDataModelElement("brack_str1", b" to horde ("),
                                IpAddressDataModelElement("ip"),
                                FixedDataModelElement("brack_str2", b")"),
                                ]),
                            SequenceModelElement("success", [
                                FixedDataModelElement("success_str", b"User "),
                                DelimitedDataModelElement("user", b" "),
                                FixedDataModelElement("brack_str1", b" logged out of Horde ("),
                                IpAddressDataModelElement("ip"),
                                FixedDataModelElement("brack_str2", b")"),
                                ]),
                            SequenceModelElement("login_failed", [
                                FixedDataModelElement("failed_str", b"FAILED LOGIN for "),
                                DelimitedDataModelElement("user", b" "),
                                FixedDataModelElement("to_horde_str", b" to horde ("),
                                IpAddressDataModelElement("ip"),
                                FixedDataModelElement("brack_str", b")"),
                                ]),
                            ])
                        ]),
                    SequenceModelElement("function", [
                        FixedWordlistDataModelElement("horde_function", [b"[nag]", b"[turba]", b"[horde]"]),
                        FixedDataModelElement("nag_str", b" PHP ERROR: "),
                        FirstMatchModelElement("php_error", [
                            SequenceModelElement("declaration", [
                                FixedDataModelElement("declaration_str", b"Declaration of "),
                                DelimitedDataModelElement("function_name1", b"("),
                                FixedDataModelElement("brack_str1", b"("),
                                OptionalMatchModelElement(
                                    "arg1", DelimitedDataModelElement("arg1", b")")
                                    ),
                                FixedDataModelElement("failed_str", b") should be compatible with "),
                                DelimitedDataModelElement("function_name2", b"("),
                                FixedDataModelElement("brack_str2", b"("),
                                OptionalMatchModelElement(
                                    "arg2", DelimitedDataModelElement("arg2", b")")
                                    ),
                                FixedDataModelElement("brack_str3", b")"),
                                ]),
                            FixedDataModelElement("file_str", b"finfo_file(): Empty filename or path"),
                            FixedDataModelElement("header_str", b"Cannot modify header information - headers already sent")
                            ])
                        ]),
                    SequenceModelElement("guest", [
                        FixedDataModelElement("guest_str", b"Guest user is not authorized for Horde (Host: "),
                        IpAddressDataModelElement("ip"),
                        FixedDataModelElement("brack_str", b").")
                        ]),
                    SequenceModelElement("php_error", [
                        FixedDataModelElement("php_error_str", b"PHP ERROR: "),
                        DelimitedDataModelElement("msg", b" ["),
                        ]),
                    SequenceModelElement("free_msg", [
                        DelimitedDataModelElement("msg", b" ["),
                        ])
                    ]),
                FixedDataModelElement("to_str", b" [pid "),
                DecimalIntegerValueModelElement("pid"),
                FixedDataModelElement("line_str", b" on line "),
                DecimalIntegerValueModelElement("line"),
                FixedDataModelElement("of_str", b' of "'),
                DelimitedDataModelElement("path", b'"'),
                FixedDataModelElement("brack_str", b'"]')
                ]),
            SequenceModelElement("cron", [
                FixedDataModelElement("cron_str", b" CRON["),
                DecimalIntegerValueModelElement("pid"),
                FixedDataModelElement("brack_str1", b"]: "),
                FirstMatchModelElement("cron", [
                    SequenceModelElement("cmd", [
                        FixedDataModelElement("brack_str", b"("),
                        DelimitedDataModelElement("user", b")"),
                        FixedDataModelElement("cmd_str", b") CMD "),
                        AnyByteDataModelElement("cmd_msg")
                        ]),
                    SequenceModelElement("session", [  # This only occurs in auth.log
                        DelimitedDataModelElement("pam", b"("),
                        FixedDataModelElement("brack_str", b"("),
                        DelimitedDataModelElement("name", b")"),
                        FixedDataModelElement("session_str", b"): session "),
                        FixedWordlistDataModelElement("status", [b"opened", b"closed"]),
                        FixedDataModelElement("user_str", b" for user "),
                        VariableByteDataModelElement("user", alphabet),
                        OptionalMatchModelElement(
                            "uid", SequenceModelElement("uid", [
                                FixedDataModelElement("uid_str", b" by (uid="),
                                DecimalIntegerValueModelElement("uid"),
                                FixedDataModelElement("brack_str", b")")
                                ])
                            )
                        ])
                    ])
                ]),
            SequenceModelElement("sudo", [
                FixedDataModelElement("cron_str", b" sudo: "),
                AnyByteDataModelElement("msg")
                ]),
            SequenceModelElement("auth", [  # This only occurs in auth.log
                FixedDataModelElement("auth_str", b" auth: "),
                DelimitedDataModelElement("pam", b"("),
                FixedDataModelElement("brack_str", b"("),
                DelimitedDataModelElement("name", b")"),
                FixedDataModelElement("session_str", b"): authentication failure; logname="),
                OptionalMatchModelElement(
                    "logname", DelimitedDataModelElement("logname", b" ")
                    ),
                FixedDataModelElement("uid_str", b" uid="),
                DecimalIntegerValueModelElement("uid"),
                FixedDataModelElement("euid_str", b" euid="),
                DecimalIntegerValueModelElement("euid"),
                FixedDataModelElement("tty_str", b" tty="),
                DelimitedDataModelElement("tty", b" "),
                FixedDataModelElement("ruser_str", b" ruser="),
                DelimitedDataModelElement("ruser", b" "),
                FixedDataModelElement("rhost_str", b" rhost="),
                IpAddressDataModelElement("rhost"),
                OptionalMatchModelElement(
                    "user", SequenceModelElement("user", [
                        FixedDataModelElement("user_str", b"  user="),
                        VariableByteDataModelElement("user", alphabet)
                        ])
                    )
                ]),
            SequenceModelElement("systemd", [
                FixedDataModelElement("systemd_str", b" systemd["),
                DecimalIntegerValueModelElement("pid"),
                FixedDataModelElement("brack_str1", b"]: "),
                AnyByteDataModelElement("msg")]),
            SequenceModelElement("systemd2", [
                FixedDataModelElement("systemd_str", b" systemd: "),
                DelimitedDataModelElement("pam", b"("),
                FixedDataModelElement("brack_str", b"("),
                DelimitedDataModelElement("name", b")"),
                FixedDataModelElement("session_str", b"): session "),
                FixedWordlistDataModelElement("status", [b"opened", b"closed"]),
                FixedDataModelElement("user_str", b" for user "),
                VariableByteDataModelElement("user", alphabet),
                OptionalMatchModelElement(
                    "uid", SequenceModelElement("uid", [
                        FixedDataModelElement("uid_str", b" by (uid="),
                        DecimalIntegerValueModelElement("uid"),
                        FixedDataModelElement("brack_str", b")")
                        ])
                    )
                ]),
            SequenceModelElement("systemd2", [
                FixedDataModelElement("systemd_str", b" sshd["),
                DecimalIntegerValueModelElement("id"),
                FixedDataModelElement("brack_str2", b"]: "),
                FirstMatchModelElement("fm", [
                    SequenceModelElement("new", [
                        FixedDataModelElement("brack_str", b"pam_unix("),
                        DelimitedDataModelElement("name", b")"),
                        FixedDataModelElement("session_str", b"): session "),
                        FixedWordlistDataModelElement("status", [b"opened", b"closed"]),
                        FixedDataModelElement("user_str", b" for user "),
                        VariableByteDataModelElement("user", alphabet),
                        OptionalMatchModelElement(
                            "uid", SequenceModelElement("uid", [
                                FixedDataModelElement("uid_str", b" by (uid="),
                                DecimalIntegerValueModelElement("uid"),
                                FixedDataModelElement("brack_str", b")")
                                ])
                            )
                        ]),
                    SequenceModelElement("publickey", [
                        FixedDataModelElement("publickey_str", b"Accepted publickey for "),
                        DelimitedDataModelElement("user", b" "),
                        FixedDataModelElement("space", b" from "),
                        IpAddressDataModelElement("ip"),
                        FixedDataModelElement("space", b" port "),
                        DecimalIntegerValueModelElement("port"),
                        FixedDataModelElement("rsa", b" ssh2: RSA "),
                        AnyByteDataModelElement("rsa"),
                        ]),
                    SequenceModelElement("ident", [
                        FixedDataModelElement("ident_str", b"Did not receive identification string from "),
                        IpAddressDataModelElement("ip"),
                        FixedDataModelElement("space", b" port "),
                        DecimalIntegerValueModelElement("port"),
                        ]),
                    SequenceModelElement("listening", [
                        FixedDataModelElement("listening_str", b"Server listening on "),
                        DelimitedDataModelElement("ip", b" "),
                        FixedDataModelElement("port_str", b" port "),
                        DecimalIntegerValueModelElement("port"),
                        FixedDataModelElement("dot", b"."),
                        ]),
                    SequenceModelElement("signal", [
                        FixedDataModelElement("signal_str", b"Received signal"),
                        AnyByteDataModelElement("remainder"),
                        ]),
                    SequenceModelElement("rec_disconnected", [
                        FixedDataModelElement("rec_disconnected_str", b"Received disconnect from "),
                        IpAddressDataModelElement("ip"),
                        FixedDataModelElement("space", b" port "),
                        DecimalIntegerValueModelElement("port"),
                        AnyByteDataModelElement("remainder"),
                        ]),
                    SequenceModelElement("disconnected", [
                        FixedDataModelElement("disconnected_str", b"Disconnected from user "),
                        DelimitedDataModelElement("user", b" "),
                        FixedDataModelElement("space", b" "),
                        IpAddressDataModelElement("ip"),
                        FixedDataModelElement("space", b" port "),
                        DecimalIntegerValueModelElement("port"),
                        ]),
                    ]),
                ]),
            SequenceModelElement("systemd2", [
                FixedDataModelElement("systemd_str", b" su["),
                DecimalIntegerValueModelElement("id"),
                FixedDataModelElement("brack_str2", b"]: "),
                FirstMatchModelElement("fm", [
                    SequenceModelElement("seq", [
                        FixedDataModelElement("brack_str", b"pam_unix("),
                        DelimitedDataModelElement("name", b")"),
                        FixedDataModelElement("session_str", b"): session "),
                        FixedWordlistDataModelElement("status", [b"opened", b"closed"]),
                        FixedDataModelElement("user_str", b" for user "),
                        VariableByteDataModelElement("user", alphabet),
                        OptionalMatchModelElement(
                            "uid", SequenceModelElement("uid", [
                                FixedDataModelElement("uid_str", b" by (uid="),
                                DecimalIntegerValueModelElement("uid"),
                                FixedDataModelElement("brack_str", b")")
                                ])
                            ),
                        ]),
                    SequenceModelElement("seq", [
                        FixedDataModelElement("brack_str", b"Successful su for "),
                        VariableByteDataModelElement("user", alphabet),
                        FixedDataModelElement("by_str", b" by "),
                        VariableByteDataModelElement("su_user", alphabet),
                        ]),
                    SequenceModelElement("seq2", [
                        FixedDataModelElement("plus", b"+"),
                        AnyByteDataModelElement("msg")
                        ]),
                    ]),
                ]),
            SequenceModelElement("kernel", [
                FixedDataModelElement("kernel_str", b" kernel"),
                OptionalMatchModelElement(
                    "id", SequenceModelElement("id", [
                        FixedDataModelElement("brack_str", b"["),
                        DecimalIntegerValueModelElement("id"),
                        FixedDataModelElement("brack_str2", b"]")
                        ])
                    ),
                FixedDataModelElement("col_str", b": "),
                AnyByteDataModelElement("kernel_msg")
                ]),
            SequenceModelElement("augenrules", [
                FixedDataModelElement("augenrules_str", b" augenrules["),
                DecimalIntegerValueModelElement("id"),
                FixedDataModelElement("brack_str1", b"]: "),
                AnyByteDataModelElement("augenrules_msg")
                ]),
            SequenceModelElement("auditd", [
                FixedDataModelElement("auditd_str", b" auditd["),
                DecimalIntegerValueModelElement("id"),
                FixedDataModelElement("brack_str1", b"]: "),
                AnyByteDataModelElement("auditd_msg")
                ]),
            SequenceModelElement("auditd2", [
                FixedDataModelElement("auditd2_str", b" auditd: "),
                AnyByteDataModelElement("auditd_msg")
                ]),
            SequenceModelElement("audispd", [
                FixedDataModelElement("audispd_str", b" audispd: "),
                AnyByteDataModelElement("audispd_msg")
                ]),
            SequenceModelElement("liblogging", [
                FixedDataModelElement("liblogging_str", b" liblogging-stdlog: "),
                AnyByteDataModelElement("liblogging_msg")
                ]),
            SequenceModelElement("os_prober", [
                FixedDataModelElement("os_prober_str", b" os-prober: "),
                AnyByteDataModelElement("os_prober_msg")
                ]),
            SequenceModelElement("macosx_prober", [
                FixedDataModelElement("macosx_prober_str", b" macosx-prober: "),
                AnyByteDataModelElement("macosx_prober_msg")
                ]),
            SequenceModelElement("haiku", [
                FixedDataModelElement("haiku_str", b" 83haiku: "),
                AnyByteDataModelElement("haiku_msg")
                ]),
            SequenceModelElement("efi", [
                FixedDataModelElement("efi_str", b" 05efi: "),
                AnyByteDataModelElement("efi_msg")
                ]),
            SequenceModelElement("freedos", [
                FixedDataModelElement("freedos_str", b" 10freedos: "),
                AnyByteDataModelElement("freedos_msg")
                ]),
            SequenceModelElement("qnx", [
                FixedDataModelElement("qnx_str", b" 10qnx: "),
                AnyByteDataModelElement("qnx_msg")
                ]),
            SequenceModelElement("microsoft", [
                FixedDataModelElement("microsoft_str", b" 20microsoft: "),
                AnyByteDataModelElement("microsoft_msg")
                ]),
            SequenceModelElement("utility", [
                FixedDataModelElement("utility_str", b" 30utility: "),
                AnyByteDataModelElement("utility_msg")
                ]),
            SequenceModelElement("mounted_tests", [
                FixedDataModelElement("mounted_tests_str", b" 50mounted-tests: "),
                AnyByteDataModelElement("mounted_tests_msg")
                ]),
            SequenceModelElement("rsyslogd", [
                FixedDataModelElement("rsyslogd_str", b" rsyslogd: "),
                AnyByteDataModelElement("rsyslogd_msg")
                ]),
            SequenceModelElement("timesyncd", [
                FixedDataModelElement("timesyncd_str", b" systemd-timesyncd["),
                DecimalIntegerValueModelElement("id"),
                FixedDataModelElement("brack_str1", b"]: "),
                AnyByteDataModelElement("timesyncd_msg")
                ]),
            SequenceModelElement("logind", [
                FixedDataModelElement("logind_str", b" systemd-logind["),
                DecimalIntegerValueModelElement("id"),
                FixedDataModelElement("brack_str1", b"]: "),
                FirstMatchModelElement("fm", [
                    SequenceModelElement("new", [
                        FixedDataModelElement("new_str", b"New session "),
                        DelimitedDataModelElement("session", b" "),
                        FixedDataModelElement("str", b" of user"),
                        AnyByteDataModelElement("user"),
                        ]),
                    SequenceModelElement("removed", [
                        FixedDataModelElement("new_str", b"Removed session "),
                        DecimalIntegerValueModelElement("session"),
                        FixedDataModelElement("dot", b"."),
                        ]),
                ])]),
            SequenceModelElement("grub", [
                FixedDataModelElement("grub_str", b" grub-common["),
                DecimalIntegerValueModelElement("id"),
                FixedDataModelElement("brack_str1", b"]:"),
                AnyByteDataModelElement("grub_msg")
                ]),
            SequenceModelElement("polkitd", [
                FixedDataModelElement("polkitd_str", b" polkitd["),
                DecimalIntegerValueModelElement("id"),
                FixedDataModelElement("brack_str1", b"]:"),
                AnyByteDataModelElement("polkitd_msg")
                ]),
            SequenceModelElement("dbus", [
                FixedDataModelElement("dbus_str", b" dbus-daemon["),
                DecimalIntegerValueModelElement("id"),
                FixedDataModelElement("brack_str1", b"]:"),
                AnyByteDataModelElement("dbus_msg")
                ]),
            SequenceModelElement("hostnamed", [
                FixedDataModelElement("hostnamed_str", b" systemd-hostnamed["),
                DecimalIntegerValueModelElement("id"),
                FixedDataModelElement("brack_str1", b"]:"),
                AnyByteDataModelElement("hostnamed_msg")
                ]),
            SequenceModelElement("apport", [
                FixedDataModelElement("apport_str", b" apport["),
                DecimalIntegerValueModelElement("id"),
                FixedDataModelElement("brack_str1", b"]:"),
                AnyByteDataModelElement("apport_msg")
                ]),
            SequenceModelElement("resolved", [
                FixedDataModelElement("resolved_str", b" systemd-resolved["),
                DecimalIntegerValueModelElement("id"),
                FixedDataModelElement("brack_str1", b"]: "),
                AnyByteDataModelElement("resolved_msg")
                ]),
            SequenceModelElement("networkd", [
                FixedDataModelElement("networkd_str", b" systemd-networkd["),
                DecimalIntegerValueModelElement("id"),
                FixedDataModelElement("brack_str1", b"]: "),
                AnyByteDataModelElement("networkd_msg")
                ]),
            SequenceModelElement("motd", [
                FixedDataModelElement("motd_str", b" 50-motd-news["),
                DecimalIntegerValueModelElement("id"),
                FixedDataModelElement("brack_str1", b"]: "),
                AnyByteDataModelElement("motd_msg")
                ]),
            SequenceModelElement("freshclam", [
                FixedDataModelElement("freshclam_str", b" freshclam["),
                DecimalIntegerValueModelElement("id"),
                FixedDataModelElement("brack_str1", b"]: "),
                AnyByteDataModelElement("freshclam_msg")
                ]),
            SequenceModelElement("dhclient", [
                FixedDataModelElement("dhclient_str", b" dhclient["),
                DecimalIntegerValueModelElement("id"),
                FixedDataModelElement("brack_str1", b"]: "),
                FirstMatchModelElement("dhclient", [
                    SequenceModelElement("dhcprequest", [
                        FixedDataModelElement("dhcprequest_str", b"DHCPREQUEST of "),
                        IpAddressDataModelElement("src_ip"),
                        FixedDataModelElement("on_str", b" on "),
                        DelimitedDataModelElement("network_interface", b" "),
                        FixedDataModelElement("to_str", b" to "),
                        IpAddressDataModelElement("dst_ip"),
                        FixedDataModelElement("port_str", b" port "),
                        DecimalIntegerValueModelElement("port")
                    ]),
                    SequenceModelElement("dhcpack", [
                        FixedDataModelElement("dhcpack_str", b"DHCPACK of "),
                        IpAddressDataModelElement("dst_ip"),
                        FixedDataModelElement("on_str", b" from "),
                        IpAddressDataModelElement("src_ip")
                    ]),
                    SequenceModelElement("bound", [
                        FixedDataModelElement("bound_str", b"bound to "),
                        IpAddressDataModelElement("ip"),
                        FixedDataModelElement("renewal_str", b" -- renewal in "),
                        DecimalIntegerValueModelElement("seconds"),
                        FixedDataModelElement("seconds_str", b" seconds.")
                        ]),
                    ]),
                ]),
            ])
        ])

    return model
