from aminer.parsing import DecimalIntegerValueModelElement
from aminer.parsing import DelimitedDataModelElement
from aminer.parsing import FirstMatchModelElement
from aminer.parsing import FixedDataModelElement
from aminer.parsing import SequenceModelElement

def getModel():
  typeChildren=[]
  typeChildren.append(SequenceModelElement('sent', [
      FixedDataModelElement('s0', 'Sent mail for '),
      DelimitedDataModelElement('to-addr', ' ('),
      FixedDataModelElement('s1', ' ('),
      DelimitedDataModelElement('status', ') uid='),
      FixedDataModelElement('s2', ') uid='),
      DecimalIntegerValueModelElement('uid'),
      FixedDataModelElement('s3', ' username='),
      DelimitedDataModelElement('username', ' outbytes='),
      FixedDataModelElement('s4', ' outbytes='),
      DecimalIntegerValueModelElement('bytes'),
  ]))

  model=SequenceModelElement('ssmtp', [
      FixedDataModelElement('sname', 'sSMTP['),
      DecimalIntegerValueModelElement('pid'),
      FixedDataModelElement('s0', ']: '),
      FirstMatchModelElement('msg', typeChildren)])
  return(model)
