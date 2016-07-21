from aminer.parsing import AnyByteDataModelElement
from aminer.parsing import DecimalIntegerValueModelElement
from aminer.parsing import FirstMatchModelElement
from aminer.parsing import FixedDataModelElement
from aminer.parsing import SequenceModelElement

def getModel():
  typeChildren=[]
  typeChildren.append(FixedDataModelElement('warn-no-openat', 'WARNING: SECURITY: No secure open yet due to missing openat in python!'))
  typeChildren.append(FixedDataModelElement('warn-no-OPATH', 'WARNING: SECURITY: Open should use O_PATH, but not yet available in python'))
  typeChildren.append(FixedDataModelElement('warn-POSIX-acls', 'WARNING: SECURITY: No checking for backdoor access via POSIX ACLs, use "getfacl" from "acl" package to check manually.'))
  typeChildren.append(FixedDataModelElement('warn-no-linkat', 'WARNING: SECURITY: unsafe unlink (unavailable unlinkat/linkat should be used, but not available in python)'))

  typeChildren.append(AnyByteDataModelElement('unparsed'))

  model=SequenceModelElement('aminer', [
      FixedDataModelElement('sname', 'AMiner['),
      DecimalIntegerValueModelElement('pid'),
      FixedDataModelElement('s0', ']: '),
      FirstMatchModelElement('msg', typeChildren)])
  return(model)
