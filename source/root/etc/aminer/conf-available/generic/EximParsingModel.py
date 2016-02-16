from aminer.parsing import AnyByteDataModelElement
from aminer.parsing import DecimalIntegerValueModelElement
from aminer.parsing import FirstMatchModelElement
from aminer.parsing import FixedDataModelElement
from aminer.parsing import FixedWordlistDataModelElement
from aminer.parsing import SequenceModelElement
from aminer.parsing import WhiteSpaceLimitedDataModelElement

def getModel(userNameModel=None):
  """This function defines how to parse a su session information message
after any standard logging preamble, e.g. from syslog."""

  typeChildren=[]
  typeChildren.append(SequenceModelElement.SequenceModelElement('queue', [
      FixedWordlistDataModelElement.FixedWordlistDataModelElement('type', ['Start', 'End']),
      FixedDataModelElement.FixedDataModelElement('s0', ' queue run: pid='),
      DecimalIntegerValueModelElement.DecimalIntegerValueModelElement('pid')]))

  typeChildren.append(SequenceModelElement.SequenceModelElement('rec-log', [
      WhiteSpaceLimitedDataModelElement.WhiteSpaceLimitedDataModelElement('id'),
      FixedDataModelElement.FixedDataModelElement('s0', ' <= '),
      WhiteSpaceLimitedDataModelElement.WhiteSpaceLimitedDataModelElement('env-from'),
      FixedDataModelElement.FixedDataModelElement('s1', ' U='),
      WhiteSpaceLimitedDataModelElement.WhiteSpaceLimitedDataModelElement('user'),
      FixedDataModelElement.FixedDataModelElement('s2', ' P='),
      WhiteSpaceLimitedDataModelElement.WhiteSpaceLimitedDataModelElement('proto'),
      FixedDataModelElement.FixedDataModelElement('s3', ' S='),
      DecimalIntegerValueModelElement.DecimalIntegerValueModelElement('size')
  ]))

  typeChildren.append(SequenceModelElement.SequenceModelElement('send-log', [
      WhiteSpaceLimitedDataModelElement.WhiteSpaceLimitedDataModelElement('id'),
      FixedDataModelElement.FixedDataModelElement('s0', ' => '),
      WhiteSpaceLimitedDataModelElement.WhiteSpaceLimitedDataModelElement('env-to'),
      FixedDataModelElement.FixedDataModelElement('s1', ' R='),
      AnyByteDataModelElement.AnyByteDataModelElement('unparsed')
  ]))

  typeChildren.append(SequenceModelElement.SequenceModelElement('sent', [
      WhiteSpaceLimitedDataModelElement.WhiteSpaceLimitedDataModelElement('id'),
      FixedDataModelElement.FixedDataModelElement('s0', ' Completed')]))

  model=SequenceModelElement.SequenceModelElement('exim', [FixedDataModelElement.FixedDataModelElement('sname', 'exim['),
      DecimalIntegerValueModelElement.DecimalIntegerValueModelElement('pid'),
      FixedDataModelElement.FixedDataModelElement('s0', ']: '),
      FirstMatchModelElement.FirstMatchModelElement('msg', typeChildren)])
  return(model)
