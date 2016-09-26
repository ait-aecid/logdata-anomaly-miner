from aminer.parsing import AnyByteDataModelElement
from aminer.parsing import DecimalIntegerValueModelElement
from aminer.parsing import FirstMatchModelElement
from aminer.parsing import FixedDataModelElement
from aminer.parsing import SequenceModelElement

def getModel():
  typeChildren=[]
  typeChildren.append(FixedDataModelElement('start', ' * Starting Tomcat servlet engine tomcat7'))
  typeChildren.append(FixedDataModelElement('stop', ' * Stopping Tomcat servlet engine tomcat7'))
  typeChildren.append(FixedDataModelElement('done', '   ...done.'))

  typeChildren.append(AnyByteDataModelElement('unparsed'))

  model=SequenceModelElement('tomcat7', [
      FixedDataModelElement('sname', 'tomcat7['),
      DecimalIntegerValueModelElement('pid'),
      FixedDataModelElement('s0', ']: '),
      FirstMatchModelElement('msg', typeChildren)])
  return(model)
