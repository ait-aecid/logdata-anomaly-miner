"""This module provides support for parsing of sshd messages."""

from aminer.parsing import DecimalIntegerValueModelElement
from aminer.parsing import DelimitedDataModelElement
from aminer.parsing import FirstMatchModelElement
from aminer.parsing import FixedDataModelElement
from aminer.parsing import FixedWordlistDataModelElement
from aminer.parsing import IpAddressDataModelElement
from aminer.parsing import OptionalMatchModelElement
from aminer.parsing import SequenceModelElement
from aminer.parsing import VariableByteDataModelElement

def getModel(userNameModel=None):
  """This function defines how to parse a sshd information message
  after any standard logging preamble, e.g. from syslog."""

  if userNameModel is None:
    userNameModel = VariableByteDataModelElement('user', b'0123456789abcdefghijklmnopqrstuvwxyz.-')

  typeChildren = []
  typeChildren.append(SequenceModelElement('accepted key', [
      FixedDataModelElement('s0', b'Accepted publickey for '),
      userNameModel,
      FixedDataModelElement('s1', b' from '),
      IpAddressDataModelElement('clientip'),
      FixedDataModelElement('s2', b' port '),
      DecimalIntegerValueModelElement('port'),
      FixedDataModelElement('s3', b' ssh2: RSA '),
      VariableByteDataModelElement(
          'fingerprint',
          b'0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ+/:')
  ]))

  typeChildren.append(SequenceModelElement('btmp-perm', [
      FixedDataModelElement('s0', b'Excess permission or bad ownership on file /var/log/btmp')
  ]))

  typeChildren.append(SequenceModelElement('close-sess', [
      FixedDataModelElement('s0', b'Close session: user '),
      userNameModel,
      FixedDataModelElement('s1', b' from '),
      IpAddressDataModelElement('clientip'),
      FixedDataModelElement('s2', b' port '),
      DecimalIntegerValueModelElement('port'),
      FixedDataModelElement('s3', b' id '),
      DecimalIntegerValueModelElement('userid')
  ]))

  typeChildren.append(SequenceModelElement('closing', [
      FixedDataModelElement('s0', b'Closing connection to '),
      IpAddressDataModelElement('clientip'),
      FixedDataModelElement('s1', b' port '),
      DecimalIntegerValueModelElement('port')]))

  typeChildren.append(SequenceModelElement('closed', [
      FixedDataModelElement('s0', b'Connection closed by '),
      IpAddressDataModelElement('clientip')]))

  typeChildren.append(SequenceModelElement('connect', [
      FixedDataModelElement('s0', b'Connection from '),
      IpAddressDataModelElement('clientip'),
      FixedDataModelElement('s1', b' port '),
      DecimalIntegerValueModelElement('port'),
      FixedDataModelElement('s2', b' on '),
      IpAddressDataModelElement('serverip'),
      FixedDataModelElement('s3', b' port '),
      DecimalIntegerValueModelElement('sport')
  ]))

  typeChildren.append(SequenceModelElement('disconnectreq', [
      FixedDataModelElement('s0', b'Received disconnect from '),
      IpAddressDataModelElement('clientip'),
      FixedDataModelElement('s1', b' port '),
      DecimalIntegerValueModelElement('port'),
      FixedDataModelElement('s2', b':'),
      DecimalIntegerValueModelElement('session'),
      FixedDataModelElement('s3', b': '),
      FixedWordlistDataModelElement('reason', [b'disconnected by user'])
  ]))

  typeChildren.append(SequenceModelElement('disconnected', [
      FixedDataModelElement('s0', b'Disconnected from '),
      IpAddressDataModelElement('clientip'),
      FixedDataModelElement('s1', b' port '),
      DecimalIntegerValueModelElement('port')
  ]))

  typeChildren.append(SequenceModelElement('error-bind', [
      FixedDataModelElement('s0', b'error: bind: Cannot assign requested address')]))

  typeChildren.append(SequenceModelElement('error-channel-setup', [
      FixedDataModelElement('s0', b'error: channel_setup_fwd_listener: cannot listen to port: '),
      DecimalIntegerValueModelElement('port')]))

  typeChildren.append(SequenceModelElement('ident-missing', [
      FixedDataModelElement('s0', b'Did not receive identification string from '),
      IpAddressDataModelElement('clientip')
  ]))

  typeChildren.append(SequenceModelElement('invalid-user', [
      FixedDataModelElement('s0', b'Invalid user '),
      DelimitedDataModelElement('user', b' from '),
      FixedDataModelElement('s1', b' from '),
      IpAddressDataModelElement('clientip')
  ]))

  typeChildren.append(SequenceModelElement('invalid-user-auth-req', [
      FixedDataModelElement('s0', b'input_userauth_request: invalid user '),
      DelimitedDataModelElement('user', b' [preauth]'),
      FixedDataModelElement('s1', b' [preauth]')
  ]))

  typeChildren.append(SequenceModelElement('postppk', [
      FixedDataModelElement('s0', b'Postponed publickey for '),
      userNameModel,
      FixedDataModelElement('s1', b' from '),
      IpAddressDataModelElement('clientip'),
      FixedDataModelElement('s2', b' port '),
      DecimalIntegerValueModelElement('port'),
      FixedDataModelElement('s3', b' ssh2 [preauth]')]))

  typeChildren.append(SequenceModelElement('readerr', [
      FixedDataModelElement('s0', b'Read error from remote host '),
      IpAddressDataModelElement('clientip'),
      FixedDataModelElement('s1', b': Connection timed out'),
  ]))

  typeChildren.append(SequenceModelElement('disconnect', [
      FixedDataModelElement('s0', b'Received disconnect from '),
      IpAddressDataModelElement('clientip'),
      FixedDataModelElement('s1', b': 11: '),
      FirstMatchModelElement('reason', [
          FixedDataModelElement('disconnected', b'disconnected by user'),
          SequenceModelElement('remotemsg', [
              DelimitedDataModelElement('msg', b' [preauth]'),
              FixedDataModelElement('s0', b' [preauth]')
          ]),
      ]),
  ]))

  typeChildren.append(SequenceModelElement('signal', [
      FixedDataModelElement('s0', b'Received signal '),
      DecimalIntegerValueModelElement('signal'),
      FixedDataModelElement('s1', b'; terminating.'),
  ]))

  typeChildren.append(SequenceModelElement('server', [
      FixedDataModelElement('s0', b'Server listening on '),
      DelimitedDataModelElement('serverip', b' '),
      FixedDataModelElement('s1', b' port '),
      DecimalIntegerValueModelElement('port'),
      FixedDataModelElement('s2', b'.'),
  ]))

  typeChildren.append(SequenceModelElement('oom-adjust', [
      FixedDataModelElement('s0', b'Set /proc/self/oom_score_adj '),
      OptionalMatchModelElement('from', FixedDataModelElement('default', b'from 0 ')),
      FixedDataModelElement('s1', b'to '),
      DecimalIntegerValueModelElement(
          'newval',
          valueSignType=DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL)
  ]))

  typeChildren.append(SequenceModelElement('session-start', [
      FixedDataModelElement('s0', b'Starting session: '),
      FirstMatchModelElement('sess-info', [
          SequenceModelElement('shell', [
              FixedDataModelElement('s0', b'shell on '),
              DelimitedDataModelElement('terminal', b' '),
          ]),
          SequenceModelElement('subsystem', [
              FixedDataModelElement('s0', b'subsystem \'sftp\''),
          ]),
          SequenceModelElement('forced-command', [
              FixedDataModelElement('s0', b'forced-command (key-option) \''),
              DelimitedDataModelElement('command', b'\' for '),
              FixedDataModelElement('s1', b'\''),
          ])
      ]),
      FixedDataModelElement('s1', b' for '),
      userNameModel,
      FixedDataModelElement('s2', b' from '),
      IpAddressDataModelElement('clientip'),
      FixedDataModelElement('s3', b' port '),
      DecimalIntegerValueModelElement('port'),
      OptionalMatchModelElement('idinfo', SequenceModelElement('idinfo', [
          FixedDataModelElement('s0', b' id '),
          DecimalIntegerValueModelElement('id')
      ]))
  ]))

  typeChildren.append(SequenceModelElement('transferred', [
      FixedDataModelElement('s0', b'Transferred: sent '),
      DecimalIntegerValueModelElement('sent'),
      FixedDataModelElement('s1', b', received '),
      DecimalIntegerValueModelElement('received'),
      FixedDataModelElement('s1', b' bytes')]))

  typeChildren.append(SequenceModelElement('pam', [
      FixedDataModelElement('s0', b'pam_unix(sshd:session): session '),
      FixedWordlistDataModelElement('change', [b'opened', b'closed']),
      FixedDataModelElement('s1', b' for user '),
      userNameModel,
      OptionalMatchModelElement('openby', FixedDataModelElement('default', b' by (uid=0)')),
  ]))

  typeChildren.append(SequenceModelElement('child', [
      FixedDataModelElement('s0', b'User child is on pid '),
      DecimalIntegerValueModelElement('pid')]))

  model = SequenceModelElement('sshd', [
      FixedDataModelElement('sname', b'sshd['),
      DecimalIntegerValueModelElement('pid'),
      FixedDataModelElement('s0', b']: '),
      FirstMatchModelElement('msg', typeChildren)])
  return model
