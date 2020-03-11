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

def get_systemd_model():
  """This function defines the parsing model for messages directly
  from systemd."""
  type_children = []
  type_children.append(FixedDataModelElement(
      'apt-daily-start', b'Starting Daily apt activities...'))

  type_children.append(FixedDataModelElement(
      'apt-daily-started', b'Started Daily apt activities.'))

  type_children.append(SequenceModelElement('apt-daily-timer', [
      FixedDataModelElement('s0', b'apt-daily.timer: Adding '),
      OptionalMatchModelElement('hopt', SequenceModelElement('hblock', [
          DecimalIntegerValueModelElement('hours'),
          FixedDataModelElement('s1', b'h '),
      ])),
      DecimalIntegerValueModelElement('minutes'),
      FixedDataModelElement('s2', b'min '),
      DecimalFloatValueModelElement('seconds'),
      FixedDataModelElement('s3', b's random time.')]))

  type_children.append(FixedDataModelElement(
      'tmp-file-cleanup', b'Starting Cleanup of Temporary Directories...'))

  type_children.append(FixedDataModelElement(
      'tmp-file-cleanup-started', b'Started Cleanup of Temporary Directories.'))

  model = SequenceModelElement('systemd', [
      FixedDataModelElement('sname', b'systemd['),
      DecimalIntegerValueModelElement('pid'),
      FixedDataModelElement('s0', b']: '),
      FirstMatchModelElement('msg', type_children)])
  return model


def get_logind_model(user_name_model=None):
  """This function defines how to parse a systemd logind daemon
  message after any standard logging preamble, e.g. from syslog."""

  if user_name_model is None:
    user_name_model = VariableByteDataModelElement(
        'user', b'0123456789abcdefghijklmnopqrstuvwxyz-')

  type_children = []
# FIXME: Will fail on username models including the dot at the end.
  type_children.append(SequenceModelElement('new session', [
      FixedDataModelElement('s0', b'New session '),
      DecimalIntegerValueModelElement('session'),
      FixedDataModelElement('s1', b' of user '),
      user_name_model,
      FixedDataModelElement('s2', b'.')]))

  type_children.append(SequenceModelElement('removed session', [
      FixedDataModelElement('s0', b'Removed session '),
      DecimalIntegerValueModelElement('session'),
      FixedDataModelElement('s1', b'.')]))

  model = SequenceModelElement('systemd-logind', [
      FixedDataModelElement('sname', b'systemd-logind['),
      DecimalIntegerValueModelElement('pid'),
      FixedDataModelElement('s0', b']: '),
      FirstMatchModelElement('msg', type_children)])
  return model


def getTmpfilesModel():
  """This function defines how to parse a systemd tmpfiles daemon
  message after any standard logging preamble, e.g. from syslog."""

  type_children = []
# FIXME: Will fail on username models including the dot at the end.
  type_children.append(SequenceModelElement('duplicate', [
      FixedDataModelElement('s0', b'[/usr/lib/tmpfiles.d/var.conf:14] Duplicate line for path "'),
      DelimitedDataModelElement('path', b'", ignoring.'),
      FixedDataModelElement('s2', b'", ignoring.')]))

  model = SequenceModelElement('systemd-tmpfiles', [
      FixedDataModelElement('sname', b'systemd-tmpfiles['),
      DecimalIntegerValueModelElement('pid'),
      FixedDataModelElement('s0', b']: '),
      FirstMatchModelElement('msg', type_children)])
  return model
