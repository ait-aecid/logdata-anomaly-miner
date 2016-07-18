from aminer.parsing import DecimalIntegerValueModelElement
from aminer.parsing import DelimitedDataModelElement
from aminer.parsing import FirstMatchModelElement
from aminer.parsing import FixedDataModelElement
from aminer.parsing import SequenceModelElement

def getModel(userNameModel=None):
  """This function defines how to parse a su session information message
after any standard logging preamble, e.g. from syslog."""

  typeChildren=[]
  typeChildren.append(SequenceModelElement('gidchange', [
      FixedDataModelElement('s0', 'rsyslogd\'s groupid changed to '),
      DecimalIntegerValueModelElement('gid')
  ]))

  typeChildren.append(SequenceModelElement('statechange', [
      FixedDataModelElement('s0', '[origin software="rsyslogd" swVersion="'),
      DelimitedDataModelElement('version', '"'),
      FixedDataModelElement('s1', '" x-pid="'),
      DecimalIntegerValueModelElement('pid'),
      FixedDataModelElement('s2', '" x-info="http://www.rsyslog.com"] '),
      FirstMatchModelElement('type', [
          FixedDataModelElement('HUPed', 'rsyslogd was HUPed'),
          FixedDataModelElement('start', 'start')
      ])
  ]))

  typeChildren.append(SequenceModelElement('uidchange', [
      FixedDataModelElement('s0', 'rsyslogd\'s userid changed to '),
      DecimalIntegerValueModelElement('uid')
  ]))

  model=SequenceModelElement('rsyslog', [
      FixedDataModelElement('sname', 'rsyslogd: '),
      FirstMatchModelElement('msg', typeChildren)])
  return(model)
