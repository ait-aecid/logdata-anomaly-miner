""" This module defines a parser for tomcat"""

from aminer.parsing import AnyByteDataModelElement
from aminer.parsing import DecimalIntegerValueModelElement
from aminer.parsing import FirstMatchModelElement
from aminer.parsing import FixedDataModelElement
from aminer.parsing import SequenceModelElement

def getModel():
  """This method returns the model."""
  typeChildren = []
  typeChildren.append(FixedDataModelElement('start', b' * Starting Tomcat servlet engine tomcat7'))
  typeChildren.append(FixedDataModelElement('stop', b' * Stopping Tomcat servlet engine tomcat7'))
  typeChildren.append(FixedDataModelElement('done', b'   ...done.'))

  typeChildren.append(AnyByteDataModelElement('unparsed'))

  model = SequenceModelElement('tomcat7', [
      FixedDataModelElement('sname', b'tomcat7['),
      DecimalIntegerValueModelElement('pid'),
      FixedDataModelElement('s0', b']: '),
      FirstMatchModelElement('msg', typeChildren)])
  return model
