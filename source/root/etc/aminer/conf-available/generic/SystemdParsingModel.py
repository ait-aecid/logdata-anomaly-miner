"""This module contains functions and classes to create the parsing
model."""

from aminer.parsing import DecimalFloatValueModelElement
from aminer.parsing import DecimalIntegerValueModelElement
from aminer.parsing import DelimitedDataModelElement
from aminer.parsing import FirstMatchModelElement
from aminer.parsing import FixedDataModelElement
from aminer.parsing import SequenceModelElement
from aminer.parsing import VariableByteDataModelElement

def getSystemdModel():
  """This function defines the parsing model for messages directly
  from systemd."""
  typeChildren = []
  typeChildren.append(FixedDataModelElement(
      'apt-daily-start', 'Starting Daily apt activities...'))

  typeChildren.append(SequenceModelElement('apt-daily-timer', [
      FixedDataModelElement('s0', 'Adding '),
      DecimalIntegerValueModelElement('hours'),
      FixedDataModelElement('s1', 'h '),
      DecimalIntegerValueModelElement('minutes'),
      FixedDataModelElement('s2', 'min '),
      DecimalFloatValueModelElement('seconds'),
      FixedDataModelElement('s3', 's random time.')]))

  typeChildren.append(FixedDataModelElement(
      'tmp-file-cleanup', 'Starting Cleanup of Temporary Directories...'))

  model = SequenceModelElement('systemd', [
      FixedDataModelElement('sname', 'systemd['),
      DecimalIntegerValueModelElement('pid'),
      FixedDataModelElement('s0', ']: '),
      FirstMatchModelElement('msg', typeChildren)])
  return model


def getLogindModel(userNameModel=None):
  """This function defines how to parse a systemd logind daemon
  message after any standard logging preamble, e.g. from syslog."""

  if userNameModel is None:
    userNameModel = VariableByteDataModelElement(
        'user', '0123456789abcdefghijklmnopqrstuvwxyz-')

  typeChildren = []
# FIXME: Will fail on username models including the dot at the end.
  typeChildren.append(SequenceModelElement('new session', [
      FixedDataModelElement('s0', 'New session '),
      DecimalIntegerValueModelElement('session'),
      FixedDataModelElement('s1', ' of user '),
      userNameModel,
      FixedDataModelElement('s2', '.')]))

  typeChildren.append(SequenceModelElement('removed session', [
      FixedDataModelElement('s0', 'Removed session '),
      DecimalIntegerValueModelElement('session'),
      FixedDataModelElement('s1', '.')]))

  model = SequenceModelElement('systemd-logind', [
      FixedDataModelElement('sname', 'systemd-logind['),
      DecimalIntegerValueModelElement('pid'),
      FixedDataModelElement('s0', ']: '),
      FirstMatchModelElement('msg', typeChildren)])
  return model


def getTmpfilesModel():
  """This function defines how to parse a systemd tmpfiles daemon
  message after any standard logging preamble, e.g. from syslog."""

  typeChildren = []
# FIXME: Will fail on username models including the dot at the end.
  typeChildren.append(SequenceModelElement('duplicate', [
      FixedDataModelElement('s0', '[/usr/lib/tmpfiles.d/var.conf:14] Duplicate line for path "'),
      DelimitedDataModelElement('path', '", ignoring.'),
      FixedDataModelElement('s2', '", ignoring.')]))

  model = SequenceModelElement('systemd-tmpfiles', [
      FixedDataModelElement('sname', 'systemd-tmpfiles['),
      DecimalIntegerValueModelElement('pid'),
      FixedDataModelElement('s0', ']: '),
      FirstMatchModelElement('msg', typeChildren)])
  return model
