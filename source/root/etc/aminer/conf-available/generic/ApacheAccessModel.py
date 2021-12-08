from aminer.parsing.DateTimeModelElement import DateTimeModelElement
from aminer.parsing.DecimalIntegerValueModelElement import DecimalIntegerValueModelElement
from aminer.parsing.FixedDataModelElement import FixedDataModelElement
from aminer.parsing.SequenceModelElement import SequenceModelElement
from aminer.parsing.VariableByteDataModelElement import VariableByteDataModelElement
from aminer.parsing.FixedWordlistDataModelElement import FixedWordlistDataModelElement
from aminer.parsing.OptionalMatchModelElement import OptionalMatchModelElement
from aminer.parsing.DelimitedDataModelElement import DelimitedDataModelElement
from aminer.parsing.FirstMatchModelElement import FirstMatchModelElement


def get_model():
    """Return a parser for apache2 access.log."""
    alphabet = b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789._-:"
    new_time_model = DateTimeModelElement("time", b"[%d/%b/%Y:%H:%M:%S%z")
    host_name_model = VariableByteDataModelElement("host", alphabet)
    identity_model = VariableByteDataModelElement("ident", alphabet)
    user_name_model = VariableByteDataModelElement("user", b"0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz.-")
    request_method_model = FirstMatchModelElement("fm", [
        FixedDataModelElement("dash", b"-"),
        SequenceModelElement("request", [
            FixedWordlistDataModelElement("method", [
                b"GET", b"POST", b"PUT", b"HEAD", b"DELETE", b"CONNECT", b"OPTIONS", b"TRACE", b"PATCH"]),
            FixedDataModelElement("sp5", b" "),
            DelimitedDataModelElement("request", b" ", b"\\"),
            FixedDataModelElement("sp6", b" "),
            DelimitedDataModelElement("version", b'"'),
            ])
        ])
    status_code_model = DecimalIntegerValueModelElement("status")
    size_model = DecimalIntegerValueModelElement("size")

    whitespace_str = b" "
    model = SequenceModelElement("accesslog", [
        host_name_model,
        FixedDataModelElement("sp0", whitespace_str),
        identity_model,
        FixedDataModelElement("sp1", whitespace_str),
        user_name_model,
        FixedDataModelElement("sp2", whitespace_str),
        new_time_model,
        FixedDataModelElement("sp3", b'] "'),
        request_method_model,
        FixedDataModelElement("sp6", b'" '),
        status_code_model,
        FixedDataModelElement("sp7", whitespace_str),
        size_model,
        OptionalMatchModelElement(
            "combined", SequenceModelElement("combined", [
                FixedDataModelElement("sp9", b' "'),
                DelimitedDataModelElement("referer", b'"', b"\\"),
                FixedDataModelElement("sp10", b'" "'),
                DelimitedDataModelElement("user_agent", b'"', b"\\"),
                FixedDataModelElement("sp11", b'"')
            ]))
        ])
    return model
