""" This module defines a parser for tomcat"""

from aminer.parsing import AnyByteDataModelElement
from aminer.parsing import DecimalIntegerValueModelElement
from aminer.parsing import FirstMatchModelElement
from aminer.parsing import FixedDataModelElement
from aminer.parsing import SequenceModelElement

def get_model():
  """This method returns the model."""
  type_children = []
  type_children.append(FixedDataModelElement('start', b' * Starting Tomcat servlet engine tomcat7'))
  type_children.append(FixedDataModelElement('stop', b' * Stopping Tomcat servlet engine tomcat7'))
  type_children.append(FixedDataModelElement('done', b'   ...done.'))

  type_children.append(AnyByteDataModelElement('unparsed'))

  model = SequenceModelElement('tomcat7', [
      FixedDataModelElement('sname', b'tomcat7['),
      DecimalIntegerValueModelElement('pid'),
      FixedDataModelElement('s0', b']: '),
      FirstMatchModelElement('msg', type_children)])
  return model
