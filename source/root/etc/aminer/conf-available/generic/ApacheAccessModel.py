"""This module defines a parser for apache2 access.log."""

from aminer.parsing import DatetimeModelElement
from aminer.parsing import DecimalIntegerValueModelElement
from aminer.parsing import FixedDataModelElement
from aminer.parsing import SequenceModelElement
from aminer.parsing import VariableByteDataModelElement
from aminer.parsing import AnyByteDataModelElement
from aminer.parsing import FixedWordlistDataModelElement


# skipcq: PYL-W0613
def get_model(new_time_model=None):

  new_time_model = DatetimeModelElement('time', b'[%d/%b/%Y:%H:%M:%S +0000]')
  host_name_model = VariableByteDataModelElement('host', b'-.01234567890abcdefghijklmnopqrstuvwxyz:')
  identity_model = VariableByteDataModelElement('ident', b'-.01234567890abcdefghijklmnopqrstuvwxyz:')
  user_name_model = VariableByteDataModelElement('user', b'0123456789abcdefghijklmnopqrstuvwxyz.-')
  request_method_model = FixedWordlistDataModelElement('method', [b'GET', b'POST', b'PUT', b'HEAD', b'DELETE', b'CONNECT', b'OPTIONS', b'TRACE', b'PATCH'])
  request_model = VariableByteDataModelElement('request', b'0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ.-/()[]{}!$%&=<?*+')
  version_model = VariableByteDataModelElement('version', b'0123456789.')
  status_code_model = DecimalIntegerValueModelElement('status')
  size_model = DecimalIntegerValueModelElement('size')
  user_agent_model = VariableByteDataModelElement('useragent', b'0123456789abcdefghijklmnopqrstuvwxyz.-/()[]{}!$%&=<?*+')

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
