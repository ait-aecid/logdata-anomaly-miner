"""This module defines a parser for apache2 access.log."""

from aminer.parsing import DateTimeModelElement
from aminer.parsing import DecimalIntegerValueModelElement
from aminer.parsing import FixedDataModelElement
from aminer.parsing import SequenceModelElement
from aminer.parsing import VariableByteDataModelElement
from aminer.parsing import AnyByteDataModelElement
from aminer.parsing import FixedWordlistDataModelElement

def getModel(timeModel=None):

  timeModel = DateTimeModelElement('time', b'[%d/%b/%Y:%H:%M:%S +0000]')
  hostNameModel = VariableByteDataModelElement('host', b'-.01234567890abcdefghijklmnopqrstuvwxyz:')
  identityModel = VariableByteDataModelElement('ident', b'-.01234567890abcdefghijklmnopqrstuvwxyz:')
  userNameModel = VariableByteDataModelElement('user', b'0123456789abcdefghijklmnopqrstuvwxyz.-')
  requestMethodModel = FixedWordlistDataModelElement('method', [b'GET', b'POST', b'PUT', b'HEAD', b'DELETE', b'CONNECT', b'OPTIONS', b'TRACE', b'PATCH'])
  requestModel = VariableByteDataModelElement('request', b'0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ.-/()[]{}!$%&=<?*+')
  versionModel = VariableByteDataModelElement('version', b'0123456789.')
  statuscodeModel = DecimalIntegerValueModelElement('status')
  sizeModel = DecimalIntegerValueModelElement('size')
  useragentModel = VariableByteDataModelElement('useragent', b'0123456789abcdefghijklmnopqrstuvwxyz.-/()[]{}!$%&=<?*+')


  model = SequenceModelElement('accesslog', [
      hostNameModel,
      FixedDataModelElement('sp0', b' '),
      identityModel,
      FixedDataModelElement('sp1', b' '),
      userNameModel,
      FixedDataModelElement('sp2', b' '),
      timeModel,
      FixedDataModelElement('sp3', b' "'),
      requestMethodModel,
      FixedDataModelElement('sp4', b' '),
      requestModel,
      FixedDataModelElement('sp5', b' HTTP/'),
      versionModel,
#      AnyByteDataModelElement('any')
      FixedDataModelElement('sp6', b'" '),
      statuscodeModel,
      FixedDataModelElement('sp7', b' '),
      sizeModel,
      FixedDataModelElement('sp8', b' "-" "'),
      useragentModel,
      FixedDataModelElement('sp9', b'"'),
      ])
  return model
