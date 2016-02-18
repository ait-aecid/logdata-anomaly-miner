from aminer.parsing import AnyByteDataModelElement
from aminer.parsing import DelimitedDataModelElement
from aminer.parsing import FirstMatchModelElement
from aminer.parsing import FixedDataModelElement
from aminer.parsing import SequenceModelElement

def getModel(messagesModel=None):
  """This function defines how to parse messages from kernel logging.
  @param if messagesModel is defined, model will first attempt
  to check if log data matches this model before returning the
  complete unparsed message as single string."""

  realMessagesModel=AnyByteDataModelElement.AnyByteDataModelElement('msg')
  if messagesModel!=None:
    realMessagesModel=FirstMatchModelElement.FirstMatchModelElement('msg', [
        messagesModel,
        realMessagesModel])

  model=SequenceModelElement.SequenceModelElement('kernel', [
      FixedDataModelElement.FixedDataModelElement('sname', 'kernel: ['),
      DelimitedDataModelElement.DelimitedDataModelElement('timestamp', ']'),
      FixedDataModelElement.FixedDataModelElement('s0', '] '),
      AnyByteDataModelElement.AnyByteDataModelElement('msg')])
  return(model)
