from aminer.parsing import DecimalIntegerValueModelElement
from aminer.parsing import FirstMatchModelElement
from aminer.parsing import FixedDataModelElement
from aminer.parsing import SequenceModelElement

def getModel(userNameModel=None):
  """This function defines how to parse a su session information message
after any standard logging preamble, e.g. from syslog."""

  typeChildren=[]
  typeChildren.append(FixedDataModelElement.FixedDataModelElement('reopen', 'reopening capture file'))
  typeChildren.append(FixedDataModelElement.FixedDataModelElement('signal', 'signal received, calling pluginstances'))

  model=SequenceModelElement.SequenceModelElement('ulogd', [FixedDataModelElement.FixedDataModelElement('sname', 'ulogd['),
      DecimalIntegerValueModelElement.DecimalIntegerValueModelElement('pid'),
      FixedDataModelElement.FixedDataModelElement('s0', ']: '),
      FirstMatchModelElement.FirstMatchModelElement('msg', typeChildren)])
  return(model)
