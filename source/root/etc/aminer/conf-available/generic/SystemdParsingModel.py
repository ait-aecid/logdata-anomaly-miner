"""This module contains functions and classes to create the parsing
model."""

from aminer.parsing import DecimalFloatValueModelElement
from aminer.parsing import DecimalIntegerValueModelElement
from aminer.parsing import DelimitedDataModelElement
from aminer.parsing import FirstMatchModelElement
from aminer.parsing import FixedDataModelElement
from aminer.parsing import OptionalMatchModelElement
from aminer.parsing import SequenceModelElement
from aminer.parsing import VariableByteDataModelElement

def getSystemdModel():
  """This function defines the parsing model for messages directly
  from systemd."""
  typeChildren = []
  typeChildren.append(FixedDataModelElement(
      'apt-daily-start', b'Starting Daily apt activities...'))

  typeChildren.append(FixedDataModelElement(
      'apt-daily-started', b'Started Daily apt activities.'))

  typeChildren.append(SequenceModelElement('apt-daily-timer', [
      FixedDataModelElement('s0', b'apt-daily.timer: Adding '),
      OptionalMatchModelElement('hopt', SequenceModelElement('hblock', [
          DecimalIntegerValueModelElement('hours'),
          FixedDataModelElement('s1', b'h '),
      ])),
      DecimalIntegerValueModelElement('minutes'),
      FixedDataModelElement('s2', b'min '),
      DecimalFloatValueModelElement('seconds'),
      FixedDataModelElement('s3', b's random time.')]))

  typeChildren.append(FixedDataModelElement(
      'tmp-file-cleanup', b'Starting Cleanup of Temporary Directories...'))

  typeChildren.append(FixedDataModelElement(
      'tmp-file-cleanup-started', b'Started Cleanup of Temporary Directories.'))

  model = SequenceModelElement('systemd', [
      FixedDataModelElement('sname', b'systemd['),
      DecimalIntegerValueModelElement('pid'),
      FixedDataModelElement('s0', b']: '),
      FirstMatchModelElement('msg', typeChildren)])
  return model


def getLogindModel(userNameModel=None):
  """This function defines how to parse a systemd logind daemon
  message after any standard logging preamble, e.g. from syslog."""

  if userNameModel is None:
    userNameModel = VariableByteDataModelElement(
        'user', b'0123456789abcdefghijklmnopqrstuvwxyz-')

  typeChildren = []
# FIXME: Will fail on username models including the dot at the end.
  typeChildren.append(SequenceModelElement('new session', [
      FixedDataModelElement('s0', b'New session '),
      DecimalIntegerValueModelElement('session'),
      FixedDataModelElement('s1', b' of user '),
      userNameModel,
      FixedDataModelElement('s2', b'.')]))

  typeChildren.append(SequenceModelElement('removed session', [
      FixedDataModelElement('s0', b'Removed session '),
      DecimalIntegerValueModelElement('session'),
      FixedDataModelElement('s1', b'.')]))

  model = SequenceModelElement('systemd-logind', [
      FixedDataModelElement('sname', b'systemd-logind['),
      DecimalIntegerValueModelElement('pid'),
      FixedDataModelElement('s0', b']: '),
      FirstMatchModelElement('msg', typeChildren)])
  return model


def getTmpfilesModel():
  """This function defines how to parse a systemd tmpfiles daemon
  message after any standard logging preamble, e.g. from syslog."""

  typeChildren = []
# FIXME: Will fail on username models including the dot at the end.
  typeChildren.append(SequenceModelElement('duplicate', [
      FixedDataModelElement('s0', b'[/usr/lib/tmpfiles.d/var.conf:14] Duplicate line for path "'),
      DelimitedDataModelElement('path', b'", ignoring.'),
      FixedDataModelElement('s2', b'", ignoring.')]))

  model = SequenceModelElement('systemd-tmpfiles', [
      FixedDataModelElement('sname', b'systemd-tmpfiles['),
      DecimalIntegerValueModelElement('pid'),
      FixedDataModelElement('s0', b']: '),
      FirstMatchModelElement('msg', typeChildren)])
  return model
