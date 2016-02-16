from aminer.parsing import DecimalIntegerValueModelElement
from aminer.parsing import DelimitedDataModelElement
from aminer.parsing import FixedDataModelElement
from aminer.parsing import SequenceModelElement

def getModel(userNameModel=None):
  """This function defines how to parse a su session information message
after any standard logging preamble, e.g. from syslog."""

  model=SequenceModelElement.SequenceModelElement('rsyslog', [
      FixedDataModelElement.FixedDataModelElement('sname', 'rsyslogd: [origin software="rsyslogd" swVersion="'),
      DelimitedDataModelElement.DelimitedDataModelElement('version', '"'),
      FixedDataModelElement.FixedDataModelElement('s0', '" x-pid="'),
      DecimalIntegerValueModelElement.DecimalIntegerValueModelElement('pid'),
      FixedDataModelElement.FixedDataModelElement('s1', '" x-info="http://www.rsyslog.com"] rsyslogd was HUPed'),
  ])
  return(model)
