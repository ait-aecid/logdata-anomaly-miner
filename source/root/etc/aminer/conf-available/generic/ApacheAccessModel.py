from aminer.parsing.DateTimeModelElement import DateTimeModelElement
from aminer.parsing.DecimalIntegerValueModelElement import DecimalIntegerValueModelElement
from aminer.parsing.FixedDataModelElement import FixedDataModelElement
from aminer.parsing.SequenceModelElement import SequenceModelElement
from aminer.parsing.VariableByteDataModelElement import VariableByteDataModelElement
from aminer.parsing.FixedWordlistDataModelElement import FixedWordlistDataModelElement


def get_model():
    """Return a parser for apache2 access.log."""
    new_time_model = SequenceModelElement('time_model', [
        DateTimeModelElement('time', b'[%d/%b/%Y:%H:%M:%S '),
        FixedWordlistDataModelElement('sign', [b'+', b'-']),
        DecimalIntegerValueModelElement('tz'),
        FixedDataModelElement('bracket', b']')])
    host_name_model = VariableByteDataModelElement('host', b'-.01234567890abcdefghijklmnopqrstuvwxyz:')
    identity_model = VariableByteDataModelElement('ident', b'-.01234567890abcdefghijklmnopqrstuvwxyz:')
    user_name_model = VariableByteDataModelElement('user', b'0123456789abcdefghijklmnopqrstuvwxyz.-')
    request_method_model = FixedWordlistDataModelElement('method', [
        b'GET', b'POST', b'PUT', b'HEAD', b'DELETE', b'CONNECT', b'OPTIONS', b'TRACE', b'PATCH'])
    request_model = VariableByteDataModelElement(
        'request', b'0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ.-/()[]{}!$%&=<?*+')
    version_model = VariableByteDataModelElement('version', b'0123456789.')
    status_code_model = DecimalIntegerValueModelElement('status')
    size_model = DecimalIntegerValueModelElement('size')
    user_agent_model = VariableByteDataModelElement(
        'useragent', b'0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ.-/()[]{}!$%&=<?*+;:_ ')

    whitespace_str = b' '
    model = SequenceModelElement('accesslog', [
        host_name_model,
        FixedDataModelElement('sp0', whitespace_str),
        identity_model,
        FixedDataModelElement('sp1', whitespace_str),
        user_name_model,
        FixedDataModelElement('sp2', whitespace_str),
        new_time_model,
        FixedDataModelElement('sp3', b' "'),
        request_method_model,
        FixedDataModelElement('sp4', whitespace_str),
        request_model,
        FixedDataModelElement('sp5', b' HTTP/'),
        version_model,
        FixedDataModelElement('sp6', b'" '),
        status_code_model,
        FixedDataModelElement('sp7', whitespace_str),
        size_model,
        FixedDataModelElement('sp8', b' "-" "'),
        user_agent_model,
        FixedDataModelElement('sp9', b'"'),
        ])
    return model
