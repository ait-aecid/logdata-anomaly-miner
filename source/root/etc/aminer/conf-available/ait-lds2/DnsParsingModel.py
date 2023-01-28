"""This module defines a generated parser model."""

from aminer.parsing.DateTimeModelElement import DateTimeModelElement
from aminer.parsing.DecimalIntegerValueModelElement import DecimalIntegerValueModelElement
from aminer.parsing.DelimitedDataModelElement import DelimitedDataModelElement
from aminer.parsing.FirstMatchModelElement import FirstMatchModelElement
from aminer.parsing.FixedDataModelElement import FixedDataModelElement
from aminer.parsing.IpAddressDataModelElement import IpAddressDataModelElement
from aminer.parsing.SequenceModelElement import SequenceModelElement
from aminer.parsing.VariableByteDataModelElement import VariableByteDataModelElement
from aminer.parsing.AnyByteDataModelElement import AnyByteDataModelElement
from aminer.parsing.DecimalFloatValueModelElement import DecimalFloatValueModelElement
from aminer.parsing.OptionalMatchModelElement import OptionalMatchModelElement


def get_model():
    """Return a model to parse Syslogs from the AIT-LDS."""
    alphabet = b"!'#$%&\"()*+,-./0123456789:;<>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ\\^_`abcdefghijklmnopqrstuvwxyz{|}~=[]"

    model = SequenceModelElement("model", [
        DateTimeModelElement("time", b"%b %d %H:%M:%S ", start_year=2022),
        DelimitedDataModelElement("service", b"["),
        FixedDataModelElement("br_open", b"["),
        DecimalIntegerValueModelElement("pid"),
        FixedDataModelElement("br_close", b"]: "),
        FirstMatchModelElement("type", [
            SequenceModelElement("query", [
                FixedDataModelElement("query", b"query["),
                VariableByteDataModelElement("record", b"ATXPRMSV"),
                FixedDataModelElement("br_close", b"] "),
                DelimitedDataModelElement("domain", b" "),
                FixedDataModelElement("from", b" from "),
                IpAddressDataModelElement("ip")
            ]),
            SequenceModelElement("reply", [
                FixedDataModelElement("reply", b"reply "),
                DelimitedDataModelElement("domain", b" "),
                FixedDataModelElement("is", b" is "),
                VariableByteDataModelElement("ip", alphabet)
            ]),
            SequenceModelElement("forwarded", [
                FixedDataModelElement("reply", b"forwarded "),
                DelimitedDataModelElement("domain", b" "),
                FixedDataModelElement("to", b" to "),
                IpAddressDataModelElement("ip")
            ]),
            SequenceModelElement("nameserver", [
                FixedDataModelElement("nameserver", b"nameserver "),
                IpAddressDataModelElement("ip"),
                FixedDataModelElement("refused", b" refused to do a recursive query"),
            ]),
            SequenceModelElement("nameserver", [
                FixedDataModelElement("nameserver", b"using nameserver "),
                IpAddressDataModelElement("ip"),
                FixedDataModelElement("port", b"#53"),
                OptionalMatchModelElement("opt_domain", SequenceModelElement("for_domain", [
                    FixedDataModelElement("for_domain", b" for domain "),
                    AnyByteDataModelElement("domain")
                ]))
            ]),
            SequenceModelElement("cached", [
                FixedDataModelElement("cached", b"cached "),
                DelimitedDataModelElement("domain", b" "),
                FixedDataModelElement("is", b" is "),
                VariableByteDataModelElement("ip", alphabet)
            ]),
            SequenceModelElement("reducing", [
                FixedDataModelElement("reducing", b"reducing DNS packet size for nameserver "),
                IpAddressDataModelElement("ip"),
                FixedDataModelElement("is", b" to "),
                DecimalIntegerValueModelElement("size")
            ]),
            SequenceModelElement("compile_time_options", [
                FixedDataModelElement("compile_time_options", b"compile time options: "),
                AnyByteDataModelElement("options")
            ]),
            SequenceModelElement("version", [
                FixedDataModelElement("version", b"started, version "),
                DecimalFloatValueModelElement("version_nr"),
                FixedDataModelElement("cachesize", b" cachesize "),
                DecimalIntegerValueModelElement("size")
            ]),
            FixedDataModelElement("read_hosts", b"read /etc/hosts - 7 addresses"),
            FixedDataModelElement("failed_access", b"failed to access /etc/dnsmasq.d/dnsmasq-resolv.conf: No such file or directory"),
            FixedDataModelElement("version.bind", b"config version.bind is <TXT>"),
        ])
    ])

    return model
