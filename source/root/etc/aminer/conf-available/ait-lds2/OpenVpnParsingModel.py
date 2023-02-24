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
from aminer.parsing.RepeatedElementDataModelElement import RepeatedElementDataModelElement
from aminer.parsing.HexStringModelElement import HexStringModelElement


def get_model():
    """Return a model to parse OpenVPN logs from the AIT-LDS2."""
    model = SequenceModelElement("model", [
        DateTimeModelElement("datetime", b"%Y-%m-%d %H:%M:%S "),
        OptionalMatchModelElement("user", SequenceModelElement("user", [
            DelimitedDataModelElement("user", b"/"),
            FixedDataModelElement("slash", b"/")
        ])),
        IpAddressDataModelElement("ip"),
        FixedDataModelElement("colon", b":"),
        DecimalIntegerValueModelElement("port"),
        FirstMatchModelElement("fm", [
            SequenceModelElement("peer_info", [
                FixedDataModelElement("peer_info_str", b" peer info: IV_"),
                FirstMatchModelElement("fm", [
                    SequenceModelElement("version", [
                        FixedDataModelElement("version_str", b"VER="),
                        AnyByteDataModelElement("version")
                        ]),
                    SequenceModelElement("platform", [
                        FixedDataModelElement("platform_str", b"PLAT="),
                        AnyByteDataModelElement("platform")
                        ]),
                    SequenceModelElement("protocol", [
                        FixedDataModelElement("protocol_str", b"PROTO="),
                        DecimalIntegerValueModelElement("protocol")
                        ]),
                    SequenceModelElement("lz", [
                        FixedWordlistDataModelElement("lz_str", [b"LZ4=", b"LZ4v2=", b"LZO="]),
                        DecimalIntegerValueModelElement("lz")
                        ]),
                    SequenceModelElement("comp_stub", [
                        FixedWordlistDataModelElement("comp_stub_str", [b"COMP_STUB=", b"COMP_STUBv2="]),
                        DecimalIntegerValueModelElement("protocol")
                        ]),
                    SequenceModelElement("tcpnl", [
                        FixedDataModelElement("tcpnl_str", b"TCPNL="),
                        DecimalIntegerValueModelElement("tcpnl")
                        ]),
                    SequenceModelElement("ncp", [
                        FixedDataModelElement("ncp_str", b"NCP="),
                        DecimalIntegerValueModelElement("ncp")
                        ]),
                    ])
                ]),
            FixedDataModelElement("validating", b" Validating certificate extended key usage"),
            SequenceModelElement("communication", [
                FixedWordlistDataModelElement("direction", [b" Outgoing Data", b" Incoming Data", b" Control"]),
                FixedDataModelElement("data_channel_str", b" Channel: "),
                AnyByteDataModelElement("msg")
                ]),
            SequenceModelElement("verify", [
                FixedDataModelElement("verify_str", b" VERIFY "),
                FixedWordlistDataModelElement("type", [b"KU", b"EKU"]),
                FixedDataModelElement("ok_str", b" OK")
                ]),
            SequenceModelElement("verify", [
                FixedDataModelElement("verify_str", b" VERIFY OK: "),
                RepeatedElementDataModelElement("cert_data", SequenceModelElement("seq", [
                    FixedWordlistDataModelElement("attribute", [b"depth", b"ST", b"L", b"O", b"CN", b"C", b"emailAddress"]),
                    FixedDataModelElement("equals_sign", b"="),
                    FirstMatchModelElement("fm", [
                        SequenceModelElement("data", [
                            DelimitedDataModelElement("data", b","),
                            FixedDataModelElement("sp", b", ")
                            ]),
                        AnyByteDataModelElement("data")
                        ]),
                    ]))
                ]),
            SequenceModelElement("tls", [
                FixedDataModelElement("tls_str", b" TLS: "),
                FirstMatchModelElement("fm", [
                    SequenceModelElement("soft_reset", [
                        FixedDataModelElement("soft_reset_str", b"soft reset sec="),
                        DecimalIntegerValueModelElement("sec"),
                        FixedDataModelElement("slash", b"/"),
                        DecimalIntegerValueModelElement("sec"),
                        FixedDataModelElement("bytes_str", b" bytes="),
                        DecimalIntegerValueModelElement("bytes"),
                        FixedDataModelElement("slash", b"/"),
                        DecimalIntegerValueModelElement("bytes", value_sign_type=DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL),
                        FixedDataModelElement("pkts_str", b" pkts="),
                        DecimalIntegerValueModelElement("pkts"),
                        FixedDataModelElement("slash", b"/"),
                        DecimalIntegerValueModelElement("pkts")
                        ]),
                    SequenceModelElement("initial_packet", [
                        FixedDataModelElement("initial_packet_str", b"Initial packet from [AF_INET]"),
                        IpAddressDataModelElement("from_ip"),
                        FixedDataModelElement("colon", b":"),
                        DecimalIntegerValueModelElement("port"),
                        FixedDataModelElement("sid_str", b", sid="),
                        HexStringModelElement("sid1"),
                        FixedDataModelElement("sp", b" "),
                        HexStringModelElement("sid2")
                        ]),
                    SequenceModelElement("move_session", [
                        FixedDataModelElement("move_session_str", b"move_session: dest="),
                        DelimitedDataModelElement("dest", b" "),
                        FixedDataModelElement("src_str", b" src="),
                        DelimitedDataModelElement("src", b" "),
                        FixedDataModelElement("reinit_src_str", b" reinit_src="),
                        DecimalIntegerValueModelElement("reinit_src")
                        ])
                    ])
                ]),
            SequenceModelElement("tls_error", [
                FixedDataModelElement("error_str", b" TLS Error: "),
                FirstMatchModelElement("fm", [
                    FixedDataModelElement("negotiation_failed",
                                          b"TLS key negotiation failed to occur within 60 seconds (check your network connectivity)"),
                    FixedDataModelElement("handshake_failed", b"TLS handshake failed")
                ])
                ]),
            SequenceModelElement("multi", [
                FixedDataModelElement("multi_str", b" MULTI: "),
                FirstMatchModelElement("fm", [
                    SequenceModelElement("learn", [
                        FixedDataModelElement("learn_str", b"Learn: "),
                        IpAddressDataModelElement("ip1"),
                        FixedDataModelElement("arrow", b" -> "),
                        DelimitedDataModelElement("name", b"/"),
                        FixedDataModelElement("slash", b"/"),
                        IpAddressDataModelElement("ip2"),
                        FixedDataModelElement("colon", b":"),
                        DecimalIntegerValueModelElement("port")
                        ]),
                    SequenceModelElement("primary", [
                        FixedDataModelElement("primary_str", b"primary virtual IP for "),
                        DelimitedDataModelElement("name", b"/"),
                        FixedDataModelElement("slash", b"/"),
                        IpAddressDataModelElement("ip1"),
                        FixedDataModelElement("colon", b":"),
                        DecimalIntegerValueModelElement("port"),
                        FixedDataModelElement("colon", b": "),
                        IpAddressDataModelElement("ip2")
                        ]),
                    ])

                ]),
            SequenceModelElement("multi_sva", [
                FixedDataModelElement("multi_str", b" MULTI_sva: "),
                FirstMatchModelElement("fm", [
                    SequenceModelElement("pool_returned", [
                        FixedDataModelElement("pool_returned_str", b"pool returned IPv4="),
                        IpAddressDataModelElement("ip"),
                        FixedDataModelElement("ipv6_str", b", IPv6="),
                        FirstMatchModelElement("fm", [
                            FixedDataModelElement("not_enabled", b"(Not enabled)"),
                            IpAddressDataModelElement("ipv6", ipv6=True)
                            ])
                        ]),
                    SequenceModelElement("primary", [
                        FixedDataModelElement("primary_str", b"primary virtual IP for "),
                        DelimitedDataModelElement("name", b"/"),
                        FixedDataModelElement("slash", b"/"),
                        IpAddressDataModelElement("ip1"),
                        FixedDataModelElement("colon", b":"),
                        DecimalIntegerValueModelElement("port"),
                        FixedDataModelElement("colon", b": "),
                        IpAddressDataModelElement("ip2")
                        ]),
                    ])

                ]),
            SequenceModelElement("activity", [
                FixedDataModelElement("open_bracket", b" ["),
                DelimitedDataModelElement("name", b"]"),
                FixedDataModelElement("close_bracket", b"] "),
                FirstMatchModelElement("fm", [
                    FixedDataModelElement("inactivity_timeout", b"Inactivity timeout (--ping-restart), restarting"),
                    SequenceModelElement("peer_conn_initiated", [
                        FixedDataModelElement("peer_conn_initiated_str", b"Peer Connection Initiated with [AF_INET]"),
                        IpAddressDataModelElement("ip"),
                        FixedDataModelElement("colon", b":"),
                        DecimalIntegerValueModelElement("port")
                        ]),
                    ])
                ]),
            SequenceModelElement("sent_control", [
                FixedDataModelElement("sent_control_str", b" SENT CONTROL ["),
                DelimitedDataModelElement("name", b"]"),
                FixedDataModelElement("bracket", b"]: "),
                AnyByteDataModelElement("msg")
                ]),
            FixedDataModelElement("client_auth_expected",
                                  b" ++ Certificate has EKU (str) TLS Web Client Authentication, expects TLS Web Client Authentication"),
            FixedDataModelElement("push", b" PUSH: Received control message: 'PUSH_REQUEST'"),
            FixedDataModelElement("SIGUSR1", b" SIGUSR1[soft,ping-restart] received, client-instance restarting")
            ])
    ])
    return model
