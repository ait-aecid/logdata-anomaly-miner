"""This module defines a parser for rsyslog"""

from aminer.parsing import DecimalIntegerValueModelElement
from aminer.parsing import DelimitedDataModelElement
from aminer.parsing import FirstMatchModelElement
from aminer.parsing import FixedDataModelElement
from aminer.parsing import SequenceModelElement

def get_model(user_name_model=None):
  """This function defines how to parse a su session information message
after any standard logging preamble, e.g. from syslog."""

  type_children = []
  type_children.append(SequenceModelElement('gidchange', [
      FixedDataModelElement('s0', b'rsyslogd\'s groupid changed to '),
      DecimalIntegerValueModelElement('gid')
  ]))

  type_children.append(SequenceModelElement('statechange', [
      FixedDataModelElement('s0', b'[origin software="rsyslogd" swVersion="'),
      DelimitedDataModelElement('version', b'"'),
      FixedDataModelElement('s1', b'" x-pid="'),
      DecimalIntegerValueModelElement('pid'),
      FixedDataModelElement('s2', b'" x-info="http://www.rsyslog.com"] '),
      FirstMatchModelElement('type', [
          FixedDataModelElement('HUPed', b'rsyslogd was HUPed'),
          FixedDataModelElement('start', b'start')
      ])
  ]))

  type_children.append(SequenceModelElement('uidchange', [
      FixedDataModelElement('s0', b'rsyslogd\'s userid changed to '),
      DecimalIntegerValueModelElement('uid')
  ]))

  model = SequenceModelElement('rsyslog', [
      FixedDataModelElement('sname', b'rsyslogd: '),
      FirstMatchModelElement('msg', type_children)])
  return model
