"""This module defines the parser for ulogd messages."""

from aminer.parsing.DecimalIntegerValueModelElement import DecimalIntegerValueModelElement
from aminer.parsing.DelimitedDataModelElement import DelimitedDataModelElement
from aminer.parsing.FirstMatchModelElement import FirstMatchModelElement
from aminer.parsing.FixedDataModelElement import FixedDataModelElement
from aminer.parsing.FixedWordlistDataModelElement import FixedWordlistDataModelElement
from aminer.parsing.IpAddressDataModelElement import IpAddressDataModelElement
from aminer.parsing.OptionalMatchModelElement import OptionalMatchModelElement
from aminer.parsing.SequenceModelElement import SequenceModelElement


def get_model():
    """Return a model for su session information messages after any standard
    logging preamble, e.g. from syslog."""
    type_children = [
        SequenceModelElement("build-stack", [
            FixedDataModelElement("s0", b"building new pluginstance stack: \""),
            DelimitedDataModelElement("stack", b"\""),
            FixedDataModelElement("s1", b"\"")
        ]),
        SequenceModelElement("nfct-event", [
            FixedDataModelElement("s0", b"[DESTROY] ORIG: SRC="),
            IpAddressDataModelElement("osrcip"),
            FixedDataModelElement("s1", b" DST="),
            IpAddressDataModelElement("odstip"),
            FixedDataModelElement("s2", b" PROTO="),
            FixedWordlistDataModelElement("proto", [b"TCP", b"UDP"]),
            FixedDataModelElement("s3", b" SPT="),
            DecimalIntegerValueModelElement("ospt"),
            FixedDataModelElement("s4", b" DPT="),
            DecimalIntegerValueModelElement("odpt"),
            FixedDataModelElement("s5", b" PKTS="),
            DecimalIntegerValueModelElement("opkts"),
            FixedDataModelElement("s6", b" BYTES="),
            DecimalIntegerValueModelElement("obytes"),
            FixedDataModelElement("s7", b" , REPLY: SRC="),
            IpAddressDataModelElement("rsrcip"),
            FixedDataModelElement("s8", b" DST="),
            IpAddressDataModelElement("rdstip"),
            FixedDataModelElement("s9", b" PROTO="),
            FixedWordlistDataModelElement("rproto", [b"TCP", b"UDP"]),
            FixedDataModelElement("s10", b" SPT="),
            DecimalIntegerValueModelElement("rspt"),
            FixedDataModelElement("s11", b" DPT="),
            DecimalIntegerValueModelElement("rdpt"),
            FixedDataModelElement("s12", b" PKTS="),
            DecimalIntegerValueModelElement("rpkts"),
            FixedDataModelElement("s13", b" BYTES="),
            DecimalIntegerValueModelElement("rbytes"),
            # No additional whitespace from Ubuntu Trusty 14.04 on.
            OptionalMatchModelElement("tail", FixedDataModelElement("s0", b" "))
        ]),
        FixedDataModelElement("nfct-plugin", b"NFCT plugin working in event mode"),
        FixedDataModelElement("reopen", b"reopening capture file"),
        FixedDataModelElement("signal", b"signal received, calling pluginstances"),
        FixedDataModelElement("uidchange", b"Changing UID / GID"),
        SequenceModelElement("seq", [
            FixedDataModelElement("s0", b"id=\""),
            DecimalIntegerValueModelElement("id"),
            FixedDataModelElement("s1", b"\" severity=\""),
            DelimitedDataModelElement("severity", b"\""),
            FixedDataModelElement("s2", b"\" sys=\""),
            DelimitedDataModelElement("sys", b"\""),
            FixedDataModelElement("s3", b"\" sub=\""),
            DelimitedDataModelElement("sub", b"\""),
            FixedDataModelElement("s4", b"\" name=\""),
            DelimitedDataModelElement("name", b"\""),
            FixedDataModelElement("s5", b"\" action=\""),
            DelimitedDataModelElement("action", b"\""),
            FixedDataModelElement("s6", b"\" fwrule=\""),
            DelimitedDataModelElement("fwrule", b"\""),
            FixedDataModelElement("s7", b"\" initf=\""),
            DelimitedDataModelElement("initf", b"\""),
            FixedDataModelElement("s8", b"\" srcmac=\""),
            DelimitedDataModelElement("srcmac", b"\""),
            FixedDataModelElement("s9", b"\" dstmac=\""),
            DelimitedDataModelElement("dstmac", b"\""),
            FixedDataModelElement("s10", b"\" srcip=\""),
            DelimitedDataModelElement("srcip", b"\""),
            FixedDataModelElement("s11", b"\" dstip=\""),
            DelimitedDataModelElement("dstip", b"\""),
            FixedDataModelElement("s12", b"\" proto=\""),
            DelimitedDataModelElement("proto", b"\""),
            FixedDataModelElement("s13", b"\" length=\""),
            DelimitedDataModelElement("length", b"\""),
            FixedDataModelElement("s14", b"\" tos=\""),
            DelimitedDataModelElement("tos", b"\""),
            FixedDataModelElement("s15", b"\" prec=\""),
            DelimitedDataModelElement("prec", b"\""),
            FixedDataModelElement("s16", b"\" ttl=\""),
            DelimitedDataModelElement("ttl", b"\""),
            FixedDataModelElement("s17", b"\" srcport=\""),
            DelimitedDataModelElement("srcport", b"\""),
            FixedDataModelElement("s18", b"\" dstport=\""),
            DelimitedDataModelElement("dstport", b"\""),
            FixedDataModelElement("s19", b"\" tcpflags=\""),
            DelimitedDataModelElement("tcpflags", b"\""),
            FixedDataModelElement("s20", b"\"")
        ])
    ]

    # Netflow entry
    model = SequenceModelElement("ulogd", [
        FixedDataModelElement("sname", b"ulogd["),
        DecimalIntegerValueModelElement("pid"),
        FixedDataModelElement("s0", b"]: "),
        FirstMatchModelElement("msg", type_children)
    ])
    return model
