"""This module defines a parser for the aminer."""

from aminer.parsing import AnyByteDataModelElement
from aminer.parsing import DecimalIntegerValueModelElement
from aminer.parsing import FirstMatchModelElement
from aminer.parsing import FixedDataModelElement
from aminer.parsing import SequenceModelElement

def getModel():
  """This method returns the model."""
  typeChildren = []
  typeChildren.append(FixedDataModelElement('warn-no-openat', \
          b'WARNING: SECURITY: No secure open yet due to missing openat in python!'))
  typeChildren.append(FixedDataModelElement('warn-no-OPATH', \
          b'WARNING: SECURITY: Open should use O_PATH, but not yet available in python'))
  typeChildren.append(FixedDataModelElement('warn-POSIX-acls', \
          b'WARNING: SECURITY: No checking for backdoor access via \
          POSIX ACLs, use "getfacl" from "acl" package to check manually.'))
  typeChildren.append(FixedDataModelElement('warn-no-linkat', \
          b'WARNING: SECURITY: unsafe unlink (unavailable unlinkat/linkat \
          should be used, but not available in python)'))

  typeChildren.append(AnyByteDataModelElement('unparsed'))

  model = SequenceModelElement('aminer', [
      FixedDataModelElement('sname', b'AMiner['),
      DecimalIntegerValueModelElement('pid'),
      FixedDataModelElement('s0', b']: '),
      FirstMatchModelElement('msg', typeChildren)])
  return model
