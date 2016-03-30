from aminer.parsing import DecimalIntegerValueModelElement
from aminer.parsing import DelimitedDataModelElement
from aminer.parsing import FirstMatchModelElement
from aminer.parsing import FixedDataModelElement
from aminer.parsing import SequenceModelElement

def getModel(userNameModel=None):
  """This function defines how to parse a su session information message
after any standard logging preamble, e.g. from syslog."""

  typeChildren=[]
  typeChildren.append(SequenceModelElement.SequenceModelElement('gidchange', [
      FixedDataModelElement.FixedDataModelElement('s0', 'rsyslogd\'s groupid changed to '),
      DecimalIntegerValueModelElement.DecimalIntegerValueModelElement('gid')
  ]))

  typeChildren.append(SequenceModelElement.SequenceModelElement('statechange', [
      FixedDataModelElement.FixedDataModelElement('s0', '[origin software="rsyslogd" swVersion="'),
      DelimitedDataModelElement.DelimitedDataModelElement('version', '"'),
      FixedDataModelElement.FixedDataModelElement('s1', '" x-pid="'),
      DecimalIntegerValueModelElement.DecimalIntegerValueModelElement('pid'),
      FixedDataModelElement.FixedDataModelElement('s2', '" x-info="http://www.rsyslog.com"] '),
      FirstMatchModelElement.FirstMatchModelElement('type', [
          FixedDataModelElement.FixedDataModelElement('HUPed', 'rsyslogd was HUPed'),
          FixedDataModelElement.FixedDataModelElement('start', 'start')
      ])
  ]))

  typeChildren.append(SequenceModelElement.SequenceModelElement('uidchange', [
      FixedDataModelElement.FixedDataModelElement('s0', 'rsyslogd\'s userid changed to '),
      DecimalIntegerValueModelElement.DecimalIntegerValueModelElement('uid')
  ]))

  model=SequenceModelElement.SequenceModelElement('rsyslog', [
      FixedDataModelElement.FixedDataModelElement('sname', 'rsyslogd: '),
      FirstMatchModelElement.FirstMatchModelElement('msg', typeChildren)])
  return(model)
