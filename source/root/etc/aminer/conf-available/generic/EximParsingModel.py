from aminer.parsing import AnyByteDataModelElement
from aminer.parsing import DecimalIntegerValueModelElement
from aminer.parsing import DelimitedDataModelElement
from aminer.parsing import FirstMatchModelElement
from aminer.parsing import FixedDataModelElement
from aminer.parsing import FixedWordlistDataModelElement
from aminer.parsing import IpAddressDataModelElement
from aminer.parsing import OptionalMatchModelElement
from aminer.parsing import SequenceModelElement
from aminer.parsing import WhiteSpaceLimitedDataModelElement

def getModel(userNameModel=None):
  """This function defines how to parse a su session information message
after any standard logging preamble, e.g. from syslog."""

  typeChildren=[]
  typeChildren.append(SequenceModelElement('queue', [
      FixedWordlistDataModelElement('type', ['Start', 'End']),
      FixedDataModelElement('s0', ' queue run: pid='),
      DecimalIntegerValueModelElement('pid')]))

  typeChildren.append(SequenceModelElement('rec-log', [
      WhiteSpaceLimitedDataModelElement('id'),
      FixedDataModelElement('s0', ' <= '),
      WhiteSpaceLimitedDataModelElement('env-from'),
      FirstMatchModelElement('source', [
          SequenceModelElement('network', [
              FixedDataModelElement('s0', ' H=('),
              DelimitedDataModelElement('hostname', ') '),
              FixedDataModelElement('s1', ') ['),
              IpAddressDataModelElement('hostip'),
              FixedDataModelElement('s2', ']')]),
          SequenceModelElement('user', [
              FixedDataModelElement('s0', ' U='),
              WhiteSpaceLimitedDataModelElement('user')])
      ]),
      FixedDataModelElement('s2', ' P='),
      WhiteSpaceLimitedDataModelElement('proto'),
      FixedDataModelElement('s3', ' S='),
      DecimalIntegerValueModelElement('size'),
      OptionalMatchModelElement('idopt', SequenceModelElement('iddata', [
          FixedDataModelElement('s0', ' id='),
          AnyByteDataModelElement('id')]))
  ]))

  typeChildren.append(SequenceModelElement('send-log', [
      WhiteSpaceLimitedDataModelElement('id'),
# Strange: first address seems to use different separator than
# second one.
      FixedWordlistDataModelElement('s0', [' => ', ' ->' ]),
      DelimitedDataModelElement('env-to', ' R='),
      FixedDataModelElement('s1', ' R='),
      WhiteSpaceLimitedDataModelElement('route'),
      FixedDataModelElement('s2', ' T='),
      WhiteSpaceLimitedDataModelElement('transport'),
      AnyByteDataModelElement('unparsed')
  ]))

  typeChildren.append(SequenceModelElement('sent', [
      WhiteSpaceLimitedDataModelElement('id'),
      FixedDataModelElement('s0', ' Completed')]))

  typeChildren.append(SequenceModelElement('started', [
      FixedDataModelElement('s0', ' exim '),
      WhiteSpaceLimitedDataModelElement('version'),
      FixedDataModelElement('s1', ' daemon started: pid='),
      DecimalIntegerValueModelElement('pid'),
      FixedDataModelElement('s2', ', -q30m, listening for SMTP on [127.0.0.1]:25')
  ]))

  model=SequenceModelElement('exim', [
      FixedDataModelElement('sname', 'exim['),
      DecimalIntegerValueModelElement('pid'),
      FixedDataModelElement('s0', ']: '),
      FirstMatchModelElement('msg', typeChildren)])
  return(model)
