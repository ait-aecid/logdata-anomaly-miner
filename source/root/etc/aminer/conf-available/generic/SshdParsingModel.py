"""This module provides support for parsing of sshd messages."""

from aminer.parsing.DecimalIntegerValueModelElement import DecimalIntegerValueModelElement
from aminer.parsing.DelimitedDataModelElement import DelimitedDataModelElement
from aminer.parsing.FirstMatchModelElement import FirstMatchModelElement
from aminer.parsing.FixedDataModelElement import FixedDataModelElement
from aminer.parsing.FixedWordlistDataModelElement import FixedWordlistDataModelElement
from aminer.parsing.IpAddressDataModelElement import IpAddressDataModelElement
from aminer.parsing.OptionalMatchModelElement import OptionalMatchModelElement
from aminer.parsing.SequenceModelElement import SequenceModelElement
from aminer.parsing.VariableByteDataModelElement import VariableByteDataModelElement
from aminer.parsing.AnyByteDataModelElement import AnyByteDataModelElement


def get_model(user_name_model=None):
    """Return a model to parse a sshd information message after any standard
    logging preamble, e.g. from syslog."""
    if user_name_model is None:
        user_name_model = VariableByteDataModelElement("user", b"0123456789abcdefghijklmnopqrstuvwxyz.-")

    from_str = b" from "
    port = b" port "
    preauth = b" [preauth]"

    type_children = [
        SequenceModelElement("accepted key", [
            FixedDataModelElement("s0", b"Accepted publickey for "),
            user_name_model,
            FixedDataModelElement("s1", from_str),
            IpAddressDataModelElement("clientip"),
            FixedDataModelElement("s2", port),
            DecimalIntegerValueModelElement("port"),
            FixedDataModelElement("s3", b" ssh2: "),
            DelimitedDataModelElement("asym-algorithm", b" ", consume_delimiter=True),
            VariableByteDataModelElement("fingerprint", b"0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ+/:"),
            OptionalMatchModelElement("opt", SequenceModelElement("seq", [
                FixedDataModelElement("s4", b" ID "),
                DelimitedDataModelElement("id", b" "),
                FixedDataModelElement("s5", b" (serial "),
                DecimalIntegerValueModelElement("serial"),
                FixedDataModelElement("s6", b") CA "),
                AnyByteDataModelElement("algorithm_details")
            ]))
        ]),
        SequenceModelElement("btmp-perm", [
            FixedDataModelElement("s0", b"Excess permission or bad ownership on file /var/log/btmp")
        ]),
        SequenceModelElement("close-sess", [
            FixedDataModelElement("s0", b"Close session: user "),
            user_name_model,
            FixedDataModelElement("s1", from_str),
            IpAddressDataModelElement("clientip"),
            FixedDataModelElement("s2", port),
            DecimalIntegerValueModelElement("port"),
            FixedDataModelElement("s3", b" id "),
            DecimalIntegerValueModelElement("userid")
        ]),
        SequenceModelElement("closing", [
            FixedDataModelElement("s0", b"Closing connection to "),
            IpAddressDataModelElement("clientip"),
            FixedDataModelElement("s1", port),
            DecimalIntegerValueModelElement("port")
        ]),
        SequenceModelElement("closed", [
            FixedDataModelElement("s0", b"Connection closed by "),
            FirstMatchModelElement("fm", [
                IpAddressDataModelElement("clientip"),
                SequenceModelElement("seq", [
                    FixedWordlistDataModelElement("user-type", [b"authenticating", b"invalid"]),
                    FixedDataModelElement("s1", b" user "),
                    DelimitedDataModelElement("user", b" "),
                    FixedDataModelElement("s2", b" "),
                    FirstMatchModelElement("fm", [
                        IpAddressDataModelElement("ip"),
                        IpAddressDataModelElement("ipv6", ipv6=True)
                    ]),
                    FixedDataModelElement("s3", b" port "),
                    DecimalIntegerValueModelElement("port"),
                    FixedDataModelElement("s4", b" [preauth]")
                ])
            ])
        ]),
        SequenceModelElement("connect", [
            FixedDataModelElement("s0", b"Connection from "),
            IpAddressDataModelElement("clientip"),
            FixedDataModelElement("s1", port),
            DecimalIntegerValueModelElement("port"),
            FixedDataModelElement("s2", b" on "),
            IpAddressDataModelElement("serverip"),
            FixedDataModelElement("s3", port),
            DecimalIntegerValueModelElement("sport")
        ]),
        SequenceModelElement("disconnectreq", [
            FixedDataModelElement("s0", b"Received disconnect from "),
            IpAddressDataModelElement("clientip"),
            FixedDataModelElement("s1", port),
            DecimalIntegerValueModelElement("port"),
            FixedDataModelElement("s2", b":"),
            DecimalIntegerValueModelElement("session"),
            FixedDataModelElement("s3", b": "),
            FixedWordlistDataModelElement("reason", [b"disconnected by user"])
        ]),
        SequenceModelElement("disconnected", [
            FixedDataModelElement("s0", b"Disconnected from "),
            IpAddressDataModelElement("clientip"),
            FixedDataModelElement("s1", port),
            DecimalIntegerValueModelElement("port")
        ]),
        FixedDataModelElement("error-bind",  b"error: bind: Cannot assign requested address"),
        SequenceModelElement("error-max-auth", [
            FixedDataModelElement("s0", b"error: maximum authentication attempts exceeded for "),
            OptionalMatchModelElement("opt", FixedDataModelElement("invalid", b"invalid user ")),
            DelimitedDataModelElement("user", b" "),
            FixedDataModelElement("s1", b" from "),
            FirstMatchModelElement("fm", [
                IpAddressDataModelElement("from_ip"),
                IpAddressDataModelElement("from_ip_v6", ipv6=True)
            ]),
            FixedDataModelElement("s2", b" port "),
            DecimalIntegerValueModelElement("port"),
            FixedDataModelElement("s3", b" ssh2 [preauth]")
        ]),
        FixedDataModelElement("error-cert-exp", b"error: Certificate invalid: expired"),
        FixedDataModelElement("error-cert-not-yet-valid", b"error: Certificate invalid: not yet valid"),
        FixedDataModelElement("error-cert-not-listed-principal", b"error: Certificate invalid: name is not a listed principal"),
        FixedDataModelElement("error-refused-by-options", b"error: Refused by certificate options"),
        SequenceModelElement("error-channel-setup", [
            FixedDataModelElement("s0", b"error: channel_setup_fwd_listener: cannot listen to port: "),
            DecimalIntegerValueModelElement("port")
        ]),
        SequenceModelElement("error-auth-key", [
            FixedDataModelElement("s0", b"error: Authentication key "),
            DelimitedDataModelElement("asym-algorithm", b" "),
            FixedDataModelElement("s1", b" "),
            DelimitedDataModelElement("hash", b" "),
            FixedDataModelElement("s2", b" revoked by file "),
            AnyByteDataModelElement("file")
        ]),
        SequenceModelElement("error-load-key", [
            FixedDataModelElement("s0", b"error: Could not load host key: "),
            AnyByteDataModelElement("file")
        ]),
        SequenceModelElement("ident-missing", [
            FixedDataModelElement("s0", b"Did not receive identification string from "),
            IpAddressDataModelElement("clientip")
        ]),
        SequenceModelElement("invalid-user", [
            FixedDataModelElement("s0", b"Invalid user "),
            DelimitedDataModelElement("user", from_str),
            FixedDataModelElement("s1", from_str),
            FirstMatchModelElement("fm", [
                IpAddressDataModelElement("from_ip"),
                IpAddressDataModelElement("from_ip_v6", ipv6=True)
            ]),
            FixedDataModelElement("s2", b" port "),
            DecimalIntegerValueModelElement("port")
        ]),
        SequenceModelElement("invalid-user-auth-req", [
            FixedDataModelElement("s0", b"input_userauth_request: invalid user "),
            DelimitedDataModelElement("user", preauth),
            FixedDataModelElement("s1", preauth)
        ]),
        SequenceModelElement("postppk", [
            FixedDataModelElement("s0", b"Postponed publickey for "),
            user_name_model,
            FixedDataModelElement("s1", from_str),
            IpAddressDataModelElement("clientip"),
            FixedDataModelElement("s2", port),
            DecimalIntegerValueModelElement("port"),
            FixedDataModelElement("s3", b" ssh2 [preauth]")
        ]),
        SequenceModelElement("readerr", [
            FixedDataModelElement("s0", b"Read error from remote host "),
            IpAddressDataModelElement("clientip"),
            FixedDataModelElement("s1", b": Connection timed out")
        ]),
        SequenceModelElement("disconnect", [
            FixedDataModelElement("s0", b"Received disconnect from "),
            FirstMatchModelElement("fm", [
                IpAddressDataModelElement("from_ip"),
                IpAddressDataModelElement("from_ip_v6", ipv6=True)
            ]),
            FixedDataModelElement("s1", b": 11: "),
            FirstMatchModelElement("reason", [
                FixedDataModelElement("disconnected", b"disconnected by user"),
                SequenceModelElement("remotemsg", [
                    DelimitedDataModelElement("msg", preauth),
                    FixedDataModelElement("s0", preauth)
                ])
            ])
        ]),
        SequenceModelElement("signal", [
            FixedDataModelElement("s0", b"Received signal "),
            DecimalIntegerValueModelElement("signal"),
            FixedDataModelElement("s1", b"; terminating.")
        ]),
        SequenceModelElement("server", [
            FixedDataModelElement("s0", b"Server listening on "),
            DelimitedDataModelElement("serverip", b" "),
            FixedDataModelElement("s1", port),
            DecimalIntegerValueModelElement("port"),
            FixedDataModelElement("s2", b".")
        ]),
        SequenceModelElement("oom-adjust", [
            FixedDataModelElement("s0", b"Set /proc/self/oom_score_adj "),
            OptionalMatchModelElement("from", FixedDataModelElement("default", b"from 0 ")),
            FixedDataModelElement("s1", b"to "),
            DecimalIntegerValueModelElement("newval", value_sign_type=DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL)
        ]),
        SequenceModelElement("session-start", [
            FixedDataModelElement("s0", b"Starting session: "),
            FirstMatchModelElement("sess-info", [
                SequenceModelElement("shell", [
                    FixedDataModelElement("s0", b"shell on "),
                    DelimitedDataModelElement("terminal", b" ")
                ]),
                SequenceModelElement("subsystem", [
                    FixedDataModelElement("s0", b"subsystem \"sftp\"")
                ]),
                SequenceModelElement("forced-command", [
                    FixedDataModelElement("s0", b"forced-command (key-option) \""),
                    DelimitedDataModelElement("command", b"\" for "),
                    FixedDataModelElement("s1", b"\"")
                ])
            ]),
            FixedDataModelElement("s1", b" for "),
            user_name_model,
            FixedDataModelElement("s2", from_str),
            IpAddressDataModelElement("clientip"),
            FixedDataModelElement("s3", port),
            DecimalIntegerValueModelElement("port"),
            OptionalMatchModelElement("idinfo", SequenceModelElement("idinfo", [
                FixedDataModelElement("s0", b" id "),
                DecimalIntegerValueModelElement("id")
            ]))
        ]),
        SequenceModelElement("transferred", [
            FixedDataModelElement("s0", b"Transferred: sent "),
            DecimalIntegerValueModelElement("sent"),
            FixedDataModelElement("s1", b", received "),
            DecimalIntegerValueModelElement("received"),
            FixedDataModelElement("s1", b" bytes")]),
        SequenceModelElement("pam", [
            FixedDataModelElement("s0", b"pam_unix(sshd:session): session "),
            FixedWordlistDataModelElement("change", [b"opened", b"closed"]),
            FixedDataModelElement("s1", b" for user "),
            user_name_model,
            OptionalMatchModelElement("openby", FixedDataModelElement("default", b" by (uid=0)"))
        ]),
        SequenceModelElement("child", [
            FixedDataModelElement("s0", b"User child is on pid "),
            DecimalIntegerValueModelElement("pid")
        ]),
        SequenceModelElement("failed/accept", [
            FixedWordlistDataModelElement("s0", [b"Failed ", b"Accepted "]),
            FixedWordlistDataModelElement("type", [b"password", b"none", b"publickey"]),
            FixedDataModelElement("s1", b" for "),
            OptionalMatchModelElement("opt", FixedDataModelElement("invalid", b"invalid user ")),
            DelimitedDataModelElement("user", b" "),
            FixedDataModelElement("s2", b" from "),
            FirstMatchModelElement("fm", [
                IpAddressDataModelElement("from_ip"),
                IpAddressDataModelElement("from_ip_v6", ipv6=True)
            ]),
            FixedDataModelElement("s3", b" port "),
            DecimalIntegerValueModelElement("port"),
            AnyByteDataModelElement("service")
        ]),
        SequenceModelElement("disconnecting", [
            FixedDataModelElement("s0", b"Disconnecting "),
            FixedWordlistDataModelElement("type", [b"authenticating", b"invalid"]),
            FixedDataModelElement("s1", b" user "),
            DelimitedDataModelElement("user", b" "),
            FixedDataModelElement("s1", b" "),
            IpAddressDataModelElement("ip"),
            FixedDataModelElement("s2", b" port "),
            DecimalIntegerValueModelElement("port"),
            FixedDataModelElement("s3", b": Too many authentication failures [preauth]")
        ]),
        SequenceModelElement("fatal", [
            FixedDataModelElement("s0", b"fatal: Timeout before authentication for "),
            IpAddressDataModelElement("ip"),
            FixedDataModelElement("s1", b" port "),
            DecimalIntegerValueModelElement("port")
        ]),
        SequenceModelElement("cert-auth", [
            FixedDataModelElement("s0", b"cert: Authentication tried for "),
            DelimitedDataModelElement("user", b" "),
            FixedDataModelElement("s1", b" with valid certificate but not from a permitted source address ("),
            IpAddressDataModelElement("ip"),
            FixedDataModelElement("s2", b")."),
        ]),
        SequenceModelElement("change-root-dir", [
            FixedDataModelElement("s0", b"Changed root directory to \""),
            DelimitedDataModelElement("root-dir", b"\""),
            FixedDataModelElement("s1", b"\"")
        ]),
        FixedDataModelElement("subsystem-request", b"subsystem request for sftp"),
        SequenceModelElement("conn-write-poll", [
            FixedDataModelElement("s0", b"packet_write_poll: Connection from "),
            IpAddressDataModelElement("from_ip"),
            FixedDataModelElement("s1", b" port "),
            DecimalIntegerValueModelElement("port"),
            FixedDataModelElement("s2", b": Host is down")
        ]),
        SequenceModelElement("debug", [
            FixedDataModelElement("s0", b"debug"),
            DecimalIntegerValueModelElement("debug-num"),
            FixedDataModelElement("s1", b": "),
            FirstMatchModelElement("fm", [
                SequenceModelElement("seq1", [
                    FixedDataModelElement("s2", b"Got "),
                    DecimalIntegerValueModelElement("num1"),
                    FixedDataModelElement("s3", b"/"),
                    DecimalIntegerValueModelElement("num2"),
                    FixedDataModelElement("s4", b" for keepalive")
                ]),
                SequenceModelElement("seq2", [
                    FixedDataModelElement("s2", b"channel "),
                    DecimalIntegerValueModelElement("channel-num"),
                    FixedDataModelElement("s3", b": request "),
                    DelimitedDataModelElement("mail", b" "),
                    FixedDataModelElement("s4", b" confirm "),
                    DecimalIntegerValueModelElement("num")
                ]),
                SequenceModelElement("seq3", [
                    FixedDataModelElement("s2", b"send packet: type "),
                    DecimalIntegerValueModelElement("packet-type")
                ]),
                SequenceModelElement("seq4", [
                    FixedDataModelElement("s2", b"receive packet: type "),
                    DecimalIntegerValueModelElement("packet-type")
                ]),
                FixedDataModelElement("do-cleanup", b"do_cleanup"),
                SequenceModelElement("seq5", [
                    FixedDataModelElement("s2", b"session_pty_cleanup: session "),
                    DecimalIntegerValueModelElement("sess-num"),
                    FixedDataModelElement("s3", b" release "),
                    AnyByteDataModelElement("file")
                ])
            ])
        ]),
        SequenceModelElement("pam_succeed_if", [
            FixedDataModelElement("s0", b"pam_succeed_if(sshd:auth): requirement \"uid >= "),
            DecimalIntegerValueModelElement("uid"),
            FixedDataModelElement("s1", b"\" not met by user \""),
            DelimitedDataModelElement("user", b"\""),
            FixedDataModelElement("s2", b"\"")
        ]),
    ]

    model = SequenceModelElement("sshd", [
        FixedDataModelElement("sname", b"sshd["),
        DecimalIntegerValueModelElement("pid"),
        FixedDataModelElement("s0", b"]: "),
        FirstMatchModelElement("msg", type_children)
    ])
    return model
