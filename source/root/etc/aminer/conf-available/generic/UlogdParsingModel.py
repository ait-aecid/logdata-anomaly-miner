"""This module defines the parser for ulogd messages."""

from aminer.parsing import DecimalIntegerValueModelElement
from aminer.parsing import DelimitedDataModelElement
from aminer.parsing import FirstMatchModelElement
from aminer.parsing import FixedDataModelElement
from aminer.parsing import FixedWordlistDataModelElement
from aminer.parsing import IpAddressDataModelElement
from aminer.parsing import OptionalMatchModelElement
from aminer.parsing import SequenceModelElement

def getModel():
  """This function defines how to parse a su session information message
after any standard logging preamble, e.g. from syslog."""

  typeChildren = []
  typeChildren.append(SequenceModelElement('build-stack', [
      FixedDataModelElement('s0', 'building new pluginstance stack: \''),
      DelimitedDataModelElement('stack', '\''),
      FixedDataModelElement('s1', '\'')
  ]))

# Netflow entry
  typeChildren.append(SequenceModelElement('nfct-event', [
      FixedDataModelElement('s0', '[DESTROY] ORIG: SRC='),
      IpAddressDataModelElement('osrcip'),
      FixedDataModelElement('s1', ' DST='),
      IpAddressDataModelElement('odstip'),
      FixedDataModelElement('s2', ' PROTO='),
      FixedWordlistDataModelElement('proto', ['TCP', 'UDP']),
      FixedDataModelElement('s3', ' SPT='),
      DecimalIntegerValueModelElement('ospt'),
      FixedDataModelElement('s4', ' DPT='),
      DecimalIntegerValueModelElement('odpt'),
      FixedDataModelElement('s5', ' PKTS='),
      DecimalIntegerValueModelElement('opkts'),
      FixedDataModelElement('s6', ' BYTES='),
      DecimalIntegerValueModelElement('obytes'),
      FixedDataModelElement('s7', ' , REPLY: SRC='),
      IpAddressDataModelElement('rsrcip'),
      FixedDataModelElement('s8', ' DST='),
      IpAddressDataModelElement('rdstip'),
      FixedDataModelElement('s9', ' PROTO='),
      FixedWordlistDataModelElement('rproto', ['TCP', 'UDP']),
      FixedDataModelElement('s10', ' SPT='),
      DecimalIntegerValueModelElement('rspt'),
      FixedDataModelElement('s11', ' DPT='),
      DecimalIntegerValueModelElement('rdpt'),
      FixedDataModelElement('s12', ' PKTS='),
      DecimalIntegerValueModelElement('rpkts'),
      FixedDataModelElement('s13', ' BYTES='),
      DecimalIntegerValueModelElement('rbytes'),
# No additional whitespace from Ubuntu Trusty 14.04 on.
      OptionalMatchModelElement('tail', FixedDataModelElement('s0', ' ')),
  ]))

  typeChildren.append(FixedDataModelElement('nfct-plugin', 'NFCT plugin working in event mode'))
  typeChildren.append(FixedDataModelElement('reopen', 'reopening capture file'))
  typeChildren.append(FixedDataModelElement('signal', 'signal received, calling pluginstances'))
  typeChildren.append(FixedDataModelElement('uidchange', 'Changing UID / GID'))

  model = SequenceModelElement('ulogd', [
      FixedDataModelElement('sname', 'ulogd['),
      DecimalIntegerValueModelElement('pid'),
      FixedDataModelElement('s0', ']: '),
      FirstMatchModelElement('msg', typeChildren)])
  return model
