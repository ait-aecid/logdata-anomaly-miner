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
  """This function defines how to parse a su session information message
after any standard logging preamble, e.g. from syslog."""

  if userNameModel == None:
    userNameModel=VariableByteDataModelElement('user', '0123456789abcdefghijklmnopqrstuvwxyz.-')

  typeChildren=[]
  typeChildren.append(SequenceModelElement('accepted key', [
      FixedDataModelElement('s0', 'Accepted publickey for '),
      userNameModel,
      FixedDataModelElement('s1', ' from '),
      IpAddressDataModelElement('clientip'),
      FixedDataModelElement('s2', ' port '),
      DecimalIntegerValueModelElement('port'),
      FixedDataModelElement('s3', ' ssh2: RSA '),
      VariableByteDataModelElement('fingerprint', '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ:')]))

  typeChildren.append(SequenceModelElement('btmp-perm', [
      FixedDataModelElement('s0', 'Excess permission or bad ownership on file /var/log/btmp')
]))

  typeChildren.append(SequenceModelElement('close-sess', [
      FixedDataModelElement('s0', 'Close session: user '),
      userNameModel,
      FixedDataModelElement('s1', ' from '),
      IpAddressDataModelElement('clientip'),
      FixedDataModelElement('s2', ' port '),
      DecimalIntegerValueModelElement('port'),
      FixedDataModelElement('s3', ' id '),
      DecimalIntegerValueModelElement('userid')
  ]))

  typeChildren.append(SequenceModelElement('closing', [
      FixedDataModelElement('s0', 'Closing connection to '),
      IpAddressDataModelElement('clientip'),
      FixedDataModelElement('s1', ' port '),
      DecimalIntegerValueModelElement('port')]))

  typeChildren.append(SequenceModelElement('closed', [
      FixedDataModelElement('s0', 'Connection closed by '),
      IpAddressDataModelElement('clientip')]))

  typeChildren.append(SequenceModelElement('connect', [
      FixedDataModelElement('s0', 'Connection from '),
      IpAddressDataModelElement('clientip'),
      FixedDataModelElement('s1', ' port '),
      DecimalIntegerValueModelElement('port'),
      FixedDataModelElement('s2', ' on '),
      IpAddressDataModelElement('serverip'),
      FixedDataModelElement('s3', ' port '),
      DecimalIntegerValueModelElement('sport')]))

  typeChildren.append(SequenceModelElement('error-bind', [
      FixedDataModelElement('s0', 'error: bind: Cannot assign requested address')]))

  typeChildren.append(SequenceModelElement('error-channel-setup', [
      FixedDataModelElement('s0', 'error: channel_setup_fwd_listener: cannot listen to port: '),
      DecimalIntegerValueModelElement('port')]))

  typeChildren.append(SequenceModelElement('ident-missing', [
      FixedDataModelElement('s0', 'Did not receive identification string from '),
      IpAddressDataModelElement('clientip')
]))

  typeChildren.append(SequenceModelElement('invalid-user', [
      FixedDataModelElement('s0', 'Invalid user '),
      DelimitedDataModelElement('user', ' from '),
      FixedDataModelElement('s1', ' from '),
      IpAddressDataModelElement('clientip')
]))

  typeChildren.append(SequenceModelElement('invalid-user-auth-req', [
      FixedDataModelElement('s0', 'input_userauth_request: invalid user '),
      DelimitedDataModelElement('user', ' [preauth]'),
      FixedDataModelElement('s1', ' [preauth]')
]))

  typeChildren.append(SequenceModelElement('postppk', [
      FixedDataModelElement('s0', 'Postponed publickey for '),
      userNameModel,
      FixedDataModelElement('s1', ' from '),
      IpAddressDataModelElement('clientip'),
      FixedDataModelElement('s2', ' port '),
      DecimalIntegerValueModelElement('port'),
      FixedDataModelElement('s3', ' ssh2 [preauth]')]))

  typeChildren.append(SequenceModelElement('readerr', [
      FixedDataModelElement('s0', 'Read error from remote host '),
      IpAddressDataModelElement('clientip'),
      FixedDataModelElement('s1', ': Connection timed out'),
  ]))

  typeChildren.append(SequenceModelElement('disconnect', [
      FixedDataModelElement('s0', 'Received disconnect from '),
      IpAddressDataModelElement('clientip'),
      FixedDataModelElement('s1', ': 11: '),
      FirstMatchModelElement('reason', [
          FixedDataModelElement('disconnected', 'disconnected by user'),
          SequenceModelElement('remotemsg', [
              DelimitedDataModelElement('msg', ' [preauth]'),
              FixedDataModelElement('s0', ' [preauth]')
          ]),
      ]),
  ]))

  typeChildren.append(SequenceModelElement('signal', [
      FixedDataModelElement('s0', 'Received signal '),
      DecimalIntegerValueModelElement('signal'),
      FixedDataModelElement('s1', '; terminating.'),
  ]))

  typeChildren.append(SequenceModelElement('server', [
      FixedDataModelElement('s0', 'Server listening on '),
      DelimitedDataModelElement('serverip', ' '),
      FixedDataModelElement('s1', ' port '),
      DecimalIntegerValueModelElement('port'),
      FixedDataModelElement('s2', '.'),
  ]))

  typeChildren.append(SequenceModelElement('oom-adjust', [
      FixedDataModelElement('s0', 'Set /proc/self/oom_score_adj '),
      OptionalMatchModelElement('from', FixedDataModelElement('default', 'from 0 ')),
      FixedDataModelElement('s1', 'to '),
      DecimalIntegerValueModelElement('newval', valueSignType=DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL)
  ]))

  typeChildren.append(SequenceModelElement('session-start', [
      FixedDataModelElement('s0', 'Starting session: '),
      FirstMatchModelElement('sess-info', [
          SequenceModelElement('shell', [
              FixedDataModelElement('s0', 'shell on '),
              DelimitedDataModelElement('terminal', ' '),
          ]),
          SequenceModelElement('subsystem', [
              FixedDataModelElement('s0', 'subsystem \'sftp\''),
          ]),
      ]),
      FixedDataModelElement('s1', ' for '),
      userNameModel,
      FixedDataModelElement('s2', ' from '),
      IpAddressDataModelElement('clientip'),
      FixedDataModelElement('s3', ' port '),
      DecimalIntegerValueModelElement('port'),
      OptionalMatchModelElement('idinfo', SequenceModelElement('idinfo', [
          FixedDataModelElement('s0', ' id '),
          DecimalIntegerValueModelElement('id')
      ]))
  ]))

  typeChildren.append(SequenceModelElement('transferred', [
      FixedDataModelElement('s0', 'Transferred: sent '),
      DecimalIntegerValueModelElement('sent'),
      FixedDataModelElement('s1', ', received '),
      DecimalIntegerValueModelElement('received'),
      FixedDataModelElement('s1', ' bytes')]))

  typeChildren.append(SequenceModelElement('pam', [
      FixedDataModelElement('s0', 'pam_unix(sshd:session): session '),
      FixedWordlistDataModelElement('change', ['opened', 'closed']),
      FixedDataModelElement('s1', ' for user '),
      userNameModel,
      OptionalMatchModelElement('openby', FixedDataModelElement('default', ' by (uid=0)')),
  ]))

  typeChildren.append(SequenceModelElement('child', [
      FixedDataModelElement('s0', 'User child is on pid '),
      DecimalIntegerValueModelElement('pid')]))

  model=SequenceModelElement('sshd', [
      FixedDataModelElement('sname', 'sshd['),
      DecimalIntegerValueModelElement('pid'),
      FixedDataModelElement('s0', ']: '),
      FirstMatchModelElement('msg', typeChildren)])
  return(model)
