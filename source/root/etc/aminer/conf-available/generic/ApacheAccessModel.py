"""This module defines a parser for apache2 access.log."""

from aminer.parsing import DateTimeModelElement
from aminer.parsing import DecimalIntegerValueModelElement
from aminer.parsing import FixedDataModelElement
from aminer.parsing import SequenceModelElement
from aminer.parsing import VariableByteDataModelElement
from aminer.parsing import FixedWordlistDataModelElement


def get_model():
    """This function defines how to parse a access message logged with Apache2."""
    whitespace_str = b' '

    model = SequenceModelElement('accesslog', [
        VariableByteDataModelElement('host', b'-.01234567890abcdefghijklmnopqrstuvwxyz:'),
        FixedDataModelElement('sp0', whitespace_str),
        VariableByteDataModelElement('ident', b'-.01234567890abcdefghijklmnopqrstuvwxyz:'),
        FixedDataModelElement('sp1', whitespace_str),
        VariableByteDataModelElement('user', b'0123456789abcdefghijklmnopqrstuvwxyz.-'),
        FixedDataModelElement('sp2', whitespace_str),
        DateTimeModelElement('time', b'[%d/%b/%Y:%H:%M:%S +0000]'),
        FixedDataModelElement('sp3', b' "'),
        FixedWordlistDataModelElement('method', [b'GET', b'POST', b'PUT', b'HEAD', b'DELETE', b'CONNECT', b'OPTIONS', b'TRACE', b'PATCH']),
        FixedDataModelElement('sp4', whitespace_str),
        VariableByteDataModelElement('request', b'0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ.-/()[]{}!$%&=<?*+'),
        FixedDataModelElement('sp5', b' HTTP/'),
        VariableByteDataModelElement('version', b'0123456789.'),
        FixedDataModelElement('sp6', b'" '),
        DecimalIntegerValueModelElement('status'),
        FixedDataModelElement('sp7', whitespace_str),
        DecimalIntegerValueModelElement('size'),
        FixedDataModelElement('sp8', b' "-" "'),
        VariableByteDataModelElement('useragent', b'0123456789abcdefghijklmnopqrstuvwxyz.-/()[]{}!$%&=<?*+'),
        FixedDataModelElement('sp9', b'"'), ])
    return model
