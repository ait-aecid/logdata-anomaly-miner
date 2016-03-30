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
    userNameModel=VariableByteDataModelElement.VariableByteDataModelElement('user', '0123456789abcdefghijklmnopqrstuvwxyz.-')

  typeChildren=[]
  typeChildren.append(SequenceModelElement.SequenceModelElement('accepted key', [FixedDataModelElement.FixedDataModelElement('s0', 'Accepted publickey for '),
      userNameModel,
      FixedDataModelElement.FixedDataModelElement('s1', ' from '),
      IpAddressDataModelElement.IpAddressDataModelElement('clientip'),
      FixedDataModelElement.FixedDataModelElement('s2', ' port '),
      DecimalIntegerValueModelElement.DecimalIntegerValueModelElement('port'),
      FixedDataModelElement.FixedDataModelElement('s3', ' ssh2: RSA '),
      VariableByteDataModelElement.VariableByteDataModelElement('user', '0123456789abcdef:')]))

  typeChildren.append(SequenceModelElement.SequenceModelElement('btmp-perm', [
      FixedDataModelElement.FixedDataModelElement('s0', 'Excess permission or bad ownership on file /var/log/btmp')
]))

  typeChildren.append(SequenceModelElement.SequenceModelElement('closing', [FixedDataModelElement.FixedDataModelElement('s0', 'Closing connection to '),
      IpAddressDataModelElement.IpAddressDataModelElement('clientip'),
      FixedDataModelElement.FixedDataModelElement('s1', ' port '),
      DecimalIntegerValueModelElement.DecimalIntegerValueModelElement('port')]))

  typeChildren.append(SequenceModelElement.SequenceModelElement('closed', [FixedDataModelElement.FixedDataModelElement('s0', 'Connection closed by '),
      IpAddressDataModelElement.IpAddressDataModelElement('clientip')]))

  typeChildren.append(SequenceModelElement.SequenceModelElement('connect', [FixedDataModelElement.FixedDataModelElement('s0', 'Connection from '),
      IpAddressDataModelElement.IpAddressDataModelElement('clientip'),
      FixedDataModelElement.FixedDataModelElement('s1', ' port '),
      DecimalIntegerValueModelElement.DecimalIntegerValueModelElement('port'),
      FixedDataModelElement.FixedDataModelElement('s2', ' on '),
      IpAddressDataModelElement.IpAddressDataModelElement('serverip'),
      FixedDataModelElement.FixedDataModelElement('s3', ' port '),
      DecimalIntegerValueModelElement.DecimalIntegerValueModelElement('sport')]))

  typeChildren.append(SequenceModelElement.SequenceModelElement('error-bind', [
      FixedDataModelElement.FixedDataModelElement('s0', 'error: bind: Cannot assign requested address')]))

  typeChildren.append(SequenceModelElement.SequenceModelElement('error-channel-setup', [
      FixedDataModelElement.FixedDataModelElement('s0', 'error: channel_setup_fwd_listener: cannot listen to port: '),
      DecimalIntegerValueModelElement.DecimalIntegerValueModelElement('port')]))

  typeChildren.append(SequenceModelElement.SequenceModelElement('ident-missing', [
      FixedDataModelElement.FixedDataModelElement('s0', 'Did not receive identification string from '),
      IpAddressDataModelElement.IpAddressDataModelElement('clientip')
]))

  typeChildren.append(SequenceModelElement.SequenceModelElement('invalid-user', [
      FixedDataModelElement.FixedDataModelElement('s0', 'Invalid user '),
      DelimitedDataModelElement.DelimitedDataModelElement('user', ' from '),
      FixedDataModelElement.FixedDataModelElement('s1', ' from '),
      IpAddressDataModelElement.IpAddressDataModelElement('clientip')
]))

  typeChildren.append(SequenceModelElement.SequenceModelElement('invalid-user-auth-req', [
      FixedDataModelElement.FixedDataModelElement('s0', 'input_userauth_request: invalid user '),
      DelimitedDataModelElement.DelimitedDataModelElement('user', ' [preauth]'),
      FixedDataModelElement.FixedDataModelElement('s1', ' [preauth]')
]))

  typeChildren.append(SequenceModelElement.SequenceModelElement('postppk', [FixedDataModelElement.FixedDataModelElement('s0', 'Postponed publickey for '),
      userNameModel,
      FixedDataModelElement.FixedDataModelElement('s1', ' from '),
      IpAddressDataModelElement.IpAddressDataModelElement('clientip'),
      FixedDataModelElement.FixedDataModelElement('s2', ' port '),
      DecimalIntegerValueModelElement.DecimalIntegerValueModelElement('port'),
      FixedDataModelElement.FixedDataModelElement('s3', ' ssh2 [preauth]')]))

  typeChildren.append(SequenceModelElement.SequenceModelElement('readerr', [
      FixedDataModelElement.FixedDataModelElement('s0', 'Read error from remote host '),
      IpAddressDataModelElement.IpAddressDataModelElement('clientip'),
      FixedDataModelElement.FixedDataModelElement('s1', ': Connection timed out'),
  ]))

  typeChildren.append(SequenceModelElement.SequenceModelElement('disconnect', [
      FixedDataModelElement.FixedDataModelElement('s0', 'Received disconnect from '),
      IpAddressDataModelElement.IpAddressDataModelElement('clientip'),
      FixedDataModelElement.FixedDataModelElement('s1', ': 11: '),
      FirstMatchModelElement.FirstMatchModelElement('reason', [
          FixedDataModelElement.FixedDataModelElement('disconnected', 'disconnected by user'),
          SequenceModelElement.SequenceModelElement('remotemsg', [
              DelimitedDataModelElement.DelimitedDataModelElement('msg', ' [preauth]'),
              FixedDataModelElement.FixedDataModelElement('s0', ' [preauth]')
          ]),
      ]),
  ]))

  typeChildren.append(SequenceModelElement.SequenceModelElement('signal', [
      FixedDataModelElement.FixedDataModelElement('s0', 'Received signal '),
      DecimalIntegerValueModelElement.DecimalIntegerValueModelElement('signal'),
      FixedDataModelElement.FixedDataModelElement('s1', '; terminating.'),
  ]))

  typeChildren.append(SequenceModelElement.SequenceModelElement('server', [
      FixedDataModelElement.FixedDataModelElement('s0', 'Server listening on '),
      DelimitedDataModelElement.DelimitedDataModelElement('serverip', ' '),
      FixedDataModelElement.FixedDataModelElement('s1', ' port '),
      DecimalIntegerValueModelElement.DecimalIntegerValueModelElement('port'),
      FixedDataModelElement.FixedDataModelElement('s2', '.'),
  ]))

  typeChildren.append(SequenceModelElement.SequenceModelElement('oom-adjust', [
      FixedDataModelElement.FixedDataModelElement('s0', 'Set /proc/self/oom_score_adj '),
      OptionalMatchModelElement.OptionalMatchModelElement('from', FixedDataModelElement.FixedDataModelElement('default', 'from 0 ')),
      FixedDataModelElement.FixedDataModelElement('s1', 'to '),
      DecimalIntegerValueModelElement.DecimalIntegerValueModelElement('newval', valueSignType=DecimalIntegerValueModelElement.DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL)
  ]))

  typeChildren.append(SequenceModelElement.SequenceModelElement('session-start', [
      FixedDataModelElement.FixedDataModelElement('s0', 'Starting session: '),
      FirstMatchModelElement.FirstMatchModelElement('sess-info', [
          SequenceModelElement.SequenceModelElement('shell', [
              FixedDataModelElement.FixedDataModelElement('s0', 'shell on '),
              DelimitedDataModelElement.DelimitedDataModelElement('terminal', ' '),
          ]),
          SequenceModelElement.SequenceModelElement('subsystem', [
              FixedDataModelElement.FixedDataModelElement('s0', 'subsystem \'sftp\''),
          ]),
      ]),
      FixedDataModelElement.FixedDataModelElement('s1', ' for '),
      userNameModel,
      FixedDataModelElement.FixedDataModelElement('s2', ' from '),
      IpAddressDataModelElement.IpAddressDataModelElement('clientip'),
      FixedDataModelElement.FixedDataModelElement('s3', ' port '),
      DecimalIntegerValueModelElement.DecimalIntegerValueModelElement('port'),
  ]))

  typeChildren.append(SequenceModelElement.SequenceModelElement('transferred', [FixedDataModelElement.FixedDataModelElement('s0', 'Transferred: sent '),
      DecimalIntegerValueModelElement.DecimalIntegerValueModelElement('sent'),
      FixedDataModelElement.FixedDataModelElement('s1', ', received '),
      DecimalIntegerValueModelElement.DecimalIntegerValueModelElement('received'),
      FixedDataModelElement.FixedDataModelElement('s1', ' bytes')]))

  typeChildren.append(SequenceModelElement.SequenceModelElement('pam', [FixedDataModelElement.FixedDataModelElement('s0', 'pam_unix(sshd:session): session '),
      FixedWordlistDataModelElement.FixedWordlistDataModelElement('change', ['opened', 'closed']),
      FixedDataModelElement.FixedDataModelElement('s1', ' for user '),
      userNameModel,
      OptionalMatchModelElement.OptionalMatchModelElement('openby', FixedDataModelElement.FixedDataModelElement('default', ' by (uid=0)')),
]))

  typeChildren.append(SequenceModelElement.SequenceModelElement('child', [FixedDataModelElement.FixedDataModelElement('s0', 'User child is on pid '),
      DecimalIntegerValueModelElement.DecimalIntegerValueModelElement('pid')]))

  model=SequenceModelElement.SequenceModelElement('sshd', [FixedDataModelElement.FixedDataModelElement('sname', 'sshd['),
      DecimalIntegerValueModelElement.DecimalIntegerValueModelElement('pid'),
      FixedDataModelElement.FixedDataModelElement('s0', ']: '),
      FirstMatchModelElement.FirstMatchModelElement('msg', typeChildren)])
  return(model)
