"""This module contains functions and classes to create the parsing
model."""

from aminer.parsing import AnyByteDataModelElement
from aminer.parsing import DecimalIntegerValueModelElement
from aminer.parsing import DelimitedDataModelElement
from aminer.parsing import ElementValueBranchModelElement
from aminer.parsing import FirstMatchModelElement
from aminer.parsing import FixedDataModelElement
from aminer.parsing import FixedWordlistDataModelElement
from aminer.parsing import HexStringModelElement
from aminer.parsing import IpAddressDataModelElement
from aminer.parsing import MatchElement
from aminer.parsing import OptionalMatchModelElement
from aminer.parsing import RepeatedElementDataModelElement
from aminer.parsing import SequenceModelElement
from aminer.parsing import VariableByteDataModelElement
from aminer.parsing import WhiteSpaceLimitedDataModelElement

def getModel():
  """This function defines how to parse a audispd message logged
via syslog after any standard logging preamble, e.g. from syslog."""

  class ExecArgumentDataModelElement(object):
    """This is a helper class for parsing the (encoded) exec argument
    strings found within audit logs."""
    def __init__(self, elementId):
      self.elementId = elementId

    def getChildElements(self):
      """Get the children of this element (none)."""
      return None

    def getMatchElement(self, path, matchContext):
      """Find the maximum number of bytes belonging to an exec
      argument.
      @return a match when at least two bytes were found including
      the delimiters."""
      data = matchContext.matchData
      matchLen = 0
      matchValue = b''
      if data[0] == ord(b'"'):
        matchLen = data.find(b'"', 1)
        if matchLen == -1:
          return None
        matchValue = data[1:matchLen]
        matchLen += 1
      elif data.startswith(b'(null)'):
        matchLen = 6
        matchValue = None
      else:
# Must be upper case hex encoded:
        nextValue = -1
        for dByte in data:
          if (dByte >= 0x30) and (dByte <= 0x39):
            dByte -= 0x30
          elif (dByte >= 0x41) and (dByte <= 0x46):
            dByte -= 0x37
          else:
            break
          if nextValue == -1:
            nextValue = (dByte<<4)
          else:
            matchValue += bytearray(((nextValue|dByte),))
            nextValue = -1
          matchLen += 1
        if nextValue != -1:
          return None

      matchData = data[:matchLen]
      matchContext.update(matchData)
      return MatchElement(
          "%s/%s" % (path, self.elementId), matchData, matchValue, None)

  pamStatusWordList = FixedWordlistDataModelElement(
      'status', [b'failed', b'success'])


  typeBranches = {}
  typeBranches['ADD_USER'] = SequenceModelElement('adduser', [
      FixedDataModelElement('s0', b' pid='),
      DecimalIntegerValueModelElement('pid'),
      FixedDataModelElement('s1', b' uid='),
      DecimalIntegerValueModelElement('uid'),
      FixedDataModelElement('s2', b' auid='),
      DecimalIntegerValueModelElement('auid'),
      FixedDataModelElement('s3', b' ses='),
      DecimalIntegerValueModelElement('ses'),
      FixedDataModelElement('s4', b' msg=\'op=adding user id='),
      DecimalIntegerValueModelElement('newuserid'),
      FixedDataModelElement('s5', b' exe="'),
      DelimitedDataModelElement('exec', b'"'),
      FixedDataModelElement('s6', b'" hostname='),
      DelimitedDataModelElement('clientname', b' '),
      FixedDataModelElement('s7', b' addr='),
      DelimitedDataModelElement('clientip', b' '),
      FixedDataModelElement('s8', b' terminal='),
      WhiteSpaceLimitedDataModelElement('terminal'),
      FixedDataModelElement('s9', b' res=success\'')
  ])

  typeBranches['BPRM_FCAPS'] = SequenceModelElement('bprmfcaps', [
      FixedDataModelElement('s0', b' fver=0 fp='),
      HexStringModelElement('fp'),
      FixedDataModelElement('s1', b' fi='),
      HexStringModelElement('fi'),
      FixedDataModelElement('s2', b' fe='),
      HexStringModelElement('fe'),
      FixedDataModelElement('s3', b' old_pp='),
      HexStringModelElement('pp-old'),
      FixedDataModelElement('s4', b' old_pi='),
      HexStringModelElement('pi-old'),
      FixedDataModelElement('s5', b' old_pe='),
      HexStringModelElement('pe-old'),
      FixedDataModelElement('s6', b' new_pp='),
      HexStringModelElement('pp-new'),
      FixedDataModelElement('s7', b' new_pi='),
      HexStringModelElement('pi-new'),
      FixedDataModelElement('s8', b' new_pe='),
      HexStringModelElement('pe-new')
  ])

  typeBranches['CONFIG_CHANGE'] = SequenceModelElement('conf-change', [
      FixedDataModelElement('s0', b' auid='),
      DecimalIntegerValueModelElement('auid'),
      FixedDataModelElement('s1', b' ses='),
      DecimalIntegerValueModelElement('ses'),
      FixedDataModelElement('s2', b' op="add rule" key=(null) list='),
      DecimalIntegerValueModelElement('list'),
      FixedDataModelElement('s3', b' res='),
      DecimalIntegerValueModelElement('result')
  ])

  typeBranches['CRED_ACQ'] = SequenceModelElement('credacq', [
      FixedDataModelElement('s0', b' pid='),
      DecimalIntegerValueModelElement('pid'),
      FixedDataModelElement('s1', b' uid='),
      DecimalIntegerValueModelElement('uid'),
      FixedDataModelElement('s2', b' auid='),
      DecimalIntegerValueModelElement('auid'),
      FixedDataModelElement('s3', b' ses='),
      DecimalIntegerValueModelElement('ses'),
      FixedDataModelElement('s4', b' msg=\'op=PAM:setcred acct="'),
      DelimitedDataModelElement('username', b'"'),
      FixedDataModelElement('s5', b'" exe="'),
      DelimitedDataModelElement('exec', b'"'),
      FixedDataModelElement('s6', b'" hostname='),
      DelimitedDataModelElement('clientname', b' '),
      FixedDataModelElement('s7', b' addr='),
      DelimitedDataModelElement('clientip', b' '),
      FixedDataModelElement('s8', b' terminal='),
      WhiteSpaceLimitedDataModelElement('terminal'),
      FixedDataModelElement('s9', b' res=success\'')
  ])

  typeBranches['CRED_DISP'] = SequenceModelElement('creddisp', [
      FixedDataModelElement('s0', b' pid='),
      DecimalIntegerValueModelElement('pid'),
      FixedDataModelElement('s1', b' uid='),
      DecimalIntegerValueModelElement('uid'),
      FixedDataModelElement('s2', b' auid='),
      DecimalIntegerValueModelElement('auid'),
      FixedDataModelElement('s3', b' ses='),
      DecimalIntegerValueModelElement('ses'),
      FixedDataModelElement('s4', b' msg=\'op=PAM:setcred acct="'),
      DelimitedDataModelElement('username', b'"'),
      FixedDataModelElement('s5', b'" exe="'),
      DelimitedDataModelElement('exec', b'"'),
      FixedDataModelElement('s6', b'" hostname='),
      DelimitedDataModelElement('clientname', b' '),
      FixedDataModelElement('s7', b' addr='),
      DelimitedDataModelElement('clientip', b' '),
      FixedDataModelElement('s8', b' terminal='),
      WhiteSpaceLimitedDataModelElement('terminal'),
      FixedDataModelElement('s9', b' res=success\'')
  ])

  typeBranches['CRED_REFR'] = SequenceModelElement('creddisp', [
      FixedDataModelElement('s0', b' pid='),
      DecimalIntegerValueModelElement('pid'),
      FixedDataModelElement('s1', b' uid='),
      DecimalIntegerValueModelElement('uid'),
      FixedDataModelElement('s2', b' auid='),
      DecimalIntegerValueModelElement('auid'),
      FixedDataModelElement('s3', b' ses='),
      DecimalIntegerValueModelElement('ses'),
      FixedDataModelElement('s4', b' msg=\'op=PAM:setcred acct="root" ' \
          b'exe="/usr/sbin/sshd" hostname='),
      IpAddressDataModelElement('clientname'),
      FixedDataModelElement('s5', b' addr='),
      IpAddressDataModelElement('clientip'),
      FixedDataModelElement('s6', b' terminal=ssh res=success\'')])

  typeBranches['CWD'] = SequenceModelElement('cwd', [
      FixedDataModelElement('s0', b'  cwd='),
      ExecArgumentDataModelElement('cwd')])

# We need a type branch here also, but there is no additional
# data in EOE records after Ubuntu Trusty any more.
  typeBranches['EOE'] = OptionalMatchModelElement(
      'eoe', FixedDataModelElement('s0', b''))

  execArgModel = SequenceModelElement('execarg', [
      FixedDataModelElement('s0', b' a'),
      DecimalIntegerValueModelElement('argn'),
      FixedDataModelElement('s1', b'='),
      ExecArgumentDataModelElement('argval')])

  typeBranches['EXECVE'] = SequenceModelElement('execve', [
      FixedDataModelElement('s0', b' argc='),
      DecimalIntegerValueModelElement('argc'),
      RepeatedElementDataModelElement('arg', execArgModel)])

  typeBranches['FD_PAIR'] = SequenceModelElement('fdpair', [
      FixedDataModelElement('s0', b' fd0='),
      DecimalIntegerValueModelElement('fd0'),
      FixedDataModelElement('s1', b' fd1='),
      DecimalIntegerValueModelElement('fd1')])

# This message differs on Ubuntu 32/64 bit variants.
  typeBranches['LOGIN'] = SequenceModelElement('login', [
      FixedDataModelElement('s0', b' pid='),
      DecimalIntegerValueModelElement('pid'),
      FixedDataModelElement('s1', b' uid='),
      DecimalIntegerValueModelElement('uid'),
      FixedWordlistDataModelElement('s2', [b' old auid=', b' old-auid=']),
      DecimalIntegerValueModelElement('auid-old'),
      FixedWordlistDataModelElement('s3', [b' new auid=', b' auid=']),
      DecimalIntegerValueModelElement('auid-new'),
      FixedWordlistDataModelElement('s4', [b' old ses=', b' old-ses=']),
      DecimalIntegerValueModelElement('ses-old'),
      FixedWordlistDataModelElement('s5', [b' new ses=', b' ses=']),
      DecimalIntegerValueModelElement('ses-new'),
      FixedDataModelElement('s6', b' res='),
      DecimalIntegerValueModelElement('result')])

  inodeInfoModelElement = SequenceModelElement('inodeinfo', [
      FixedDataModelElement('s0', b' inode='),
      DecimalIntegerValueModelElement('inode'),
      FixedDataModelElement('s1', b' dev='),
      # A special major/minor device element could be better here.
      VariableByteDataModelElement('dev', b'0123456789abcdef:'),
      FixedDataModelElement('s2', b' mode='),
      # FIXME: is octal
      DecimalIntegerValueModelElement('mode'),
      FixedDataModelElement('s3', b' ouid='),
      DecimalIntegerValueModelElement('ouid'),
      FixedDataModelElement('s4', b' ogid='),
      DecimalIntegerValueModelElement('ogid'),
      FixedDataModelElement('s5', b' rdev='),
      # A special major/minor device element could be better here (see above).
      VariableByteDataModelElement('rdev', b'0123456789abcdef:'),
      FixedDataModelElement('s6', b' nametype=')])

  typeBranches['NETFILTER_CFG'] = SequenceModelElement('conf-change', [
      FixedDataModelElement('s0', b' table='),
      FixedWordlistDataModelElement('table', [b'filter', b'mangle', b'nat']),
      FixedDataModelElement('s1', b' family='),
      DecimalIntegerValueModelElement('family'),
      FixedDataModelElement('s2', b' entries='),
      DecimalIntegerValueModelElement('entries')
  ])

  typeBranches['OBJ_PID'] = SequenceModelElement('objpid', [
      FixedDataModelElement('s0', b' opid='),
      DecimalIntegerValueModelElement('opid'),
      FixedDataModelElement('s1', b' oauid='),
      DecimalIntegerValueModelElement(
          'oauid',
          valueSignType=DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL),
      FixedDataModelElement('s2', b' ouid='),
      DecimalIntegerValueModelElement('ouid'),
      FixedDataModelElement('s3', b' oses='),
      DecimalIntegerValueModelElement(
          'oses',
          valueSignType=DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL),
      FixedDataModelElement('s4', b' ocomm='),
      ExecArgumentDataModelElement('ocomm'),
  ])

  typeBranches['PATH'] = SequenceModelElement('path', [
      FixedDataModelElement('s0', b' item='),
      DecimalIntegerValueModelElement('item'),
      FixedDataModelElement('s1', b' name='),
      ExecArgumentDataModelElement('name'),
      FirstMatchModelElement('fsinfo', [
          inodeInfoModelElement,
          FixedDataModelElement('noinfo', b' nametype=')]),
      FixedWordlistDataModelElement(
          'nametype', [b'CREATE', b'DELETE', b'NORMAL', b'PARENT', b'UNKNOWN']),
  ])

  typeBranches['PROCTITLE'] = SequenceModelElement('proctitle', [
      FixedDataModelElement('s1', b' proctitle='),
      ExecArgumentDataModelElement('proctitle')])

  typeBranches['SERVICE_START'] = SequenceModelElement('service', [
      FixedDataModelElement('s0', b' pid='),
      DecimalIntegerValueModelElement('pid'),
      FixedDataModelElement('s1', b' uid='),
      DecimalIntegerValueModelElement('uid'),
      FixedDataModelElement('s2', b' auid='),
      DecimalIntegerValueModelElement('auid'),
      FixedDataModelElement('s3', b' ses='),
      DecimalIntegerValueModelElement('ses'),
      FixedDataModelElement('s4', b' msg=\'unit='),
      DelimitedDataModelElement('unit', b' '),
      FixedDataModelElement('s5', b' comm="systemd" exe="'),
      DelimitedDataModelElement('exec', b'"'),
      FixedDataModelElement('s6', b'" hostname='),
      DelimitedDataModelElement('clientname', b' '),
      FixedDataModelElement('s7', b' addr='),
      DelimitedDataModelElement('clientip', b' '),
      FixedDataModelElement('s8', b' terminal='),
      WhiteSpaceLimitedDataModelElement('terminal'),
      FixedDataModelElement('s9', b' res='),
      pamStatusWordList,
      FixedDataModelElement('s10', b'\'')
  ])
  typeBranches['SERVICE_STOP'] = typeBranches['SERVICE_START']

  typeBranches['SOCKADDR'] = SequenceModelElement('sockaddr', [
      FixedDataModelElement('s0', b' saddr='),
      HexStringModelElement('sockaddr', upperCase=True),
  ])

  typeBranches['SYSCALL'] = SequenceModelElement('syscall', [
      FixedDataModelElement('s0', b' arch='),
      HexStringModelElement('arch'),
      FixedDataModelElement('s1', b' syscall='),
      DecimalIntegerValueModelElement('syscall'),
      OptionalMatchModelElement('personality', SequenceModelElement('pseq', [
          FixedDataModelElement('s0', b' per='),
          DecimalIntegerValueModelElement('personality'),
      ])),
      OptionalMatchModelElement('result', SequenceModelElement('rseq', [
          FixedDataModelElement('s2', b' success='),
          FixedWordlistDataModelElement('succes', [b'no', b'yes']),
          FixedDataModelElement('s3', b' exit='),
          DecimalIntegerValueModelElement(
              'exit',
              valueSignType=DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL),
      ])),
      FixedDataModelElement('s4', b' a0='),
      HexStringModelElement('arg0'),
      FixedDataModelElement('s5', b' a1='),
      HexStringModelElement('arg1'),
      FixedDataModelElement('s6', b' a2='),
      HexStringModelElement('arg2'),
      FixedDataModelElement('s7', b' a3='),
      HexStringModelElement('arg3'),
      FixedDataModelElement('s8', b' items='),
      DecimalIntegerValueModelElement('items'),
      FixedDataModelElement('s9', b' ppid='),
      DecimalIntegerValueModelElement('ppid'),
      FixedDataModelElement('s10', b' pid='),
      DecimalIntegerValueModelElement('pid'),
      FixedDataModelElement('s11', b' auid='),
      DecimalIntegerValueModelElement('auid'),
      FixedDataModelElement('s12', b' uid='),
      DecimalIntegerValueModelElement('uid'),
      FixedDataModelElement('s13', b' gid='),
      DecimalIntegerValueModelElement('gid'),
      FixedDataModelElement('s14', b' euid='),
      DecimalIntegerValueModelElement('euid'),
      FixedDataModelElement('s15', b' suid='),
      DecimalIntegerValueModelElement('suid'),
      FixedDataModelElement('s16', b' fsuid='),
      DecimalIntegerValueModelElement('fsuid'),
      FixedDataModelElement('s17', b' egid='),
      DecimalIntegerValueModelElement('egid'),
      FixedDataModelElement('s18', b' sgid='),
      DecimalIntegerValueModelElement('sgid'),
      FixedDataModelElement('s19', b' fsgid='),
      DecimalIntegerValueModelElement('fsgid'),
      FixedDataModelElement('s20', b' tty='),
      DelimitedDataModelElement('tty', b' '),
      FixedDataModelElement('s21', b' ses='),
      DecimalIntegerValueModelElement('sesid'),
      FixedDataModelElement('s22', b' comm='),
      ExecArgumentDataModelElement('command'),
      FixedDataModelElement('s23', b' exe="'),
      DelimitedDataModelElement('executable', b'"'),
      FixedDataModelElement('s24', b'" key='),
      AnyByteDataModelElement('key')
  ])

# The UNKNOWN type is used then audispd does not know the type
# of the event, usually because the kernel is more recent than
# audispd, thus emiting yet unknown event types.
# * type=1327: procitle: see https://www.redhat.com/archives/linux-audit/2014-February/msg00047.html
  typeBranches['UNKNOWN[1327]'] = SequenceModelElement('unknown-proctitle', [
      FixedDataModelElement('s0', b' proctitle='),
      ExecArgumentDataModelElement('proctitle')
  ])

  typeBranches['USER_ACCT'] = SequenceModelElement('useracct', [
      FixedDataModelElement('s0', b' pid='),
      DecimalIntegerValueModelElement('pid'),
      FixedDataModelElement('s1', b' uid='),
      DecimalIntegerValueModelElement('uid'),
      FixedDataModelElement('s2', b' auid='),
      DecimalIntegerValueModelElement('auid'),
      FixedDataModelElement('s3', b' ses='),
      DecimalIntegerValueModelElement('ses'),
      FixedDataModelElement('s4', b' msg=\'op=PAM:accounting acct="'),
      DelimitedDataModelElement('username', b'"'),
      FixedDataModelElement('s5', b'" exe="'),
      DelimitedDataModelElement('exec', b'"'),
      FixedDataModelElement('s6', b'" hostname='),
      DelimitedDataModelElement('clientname', b' '),
      FixedDataModelElement('s7', b' addr='),
      DelimitedDataModelElement('clientip', b' '),
      FixedDataModelElement('s8', b' terminal='),
      WhiteSpaceLimitedDataModelElement('terminal'),
      FixedDataModelElement('s9', b' res=success\'')
  ])

  typeBranches['USER_AUTH'] = SequenceModelElement('userauth', [
      FixedDataModelElement('s0', b' pid='),
      DecimalIntegerValueModelElement('pid'),
      FixedDataModelElement('s1', b' uid='),
      DecimalIntegerValueModelElement('uid'),
      FixedDataModelElement('s2', b' auid='),
      DecimalIntegerValueModelElement('auid'),
      FixedDataModelElement('s3', b' ses='),
      DecimalIntegerValueModelElement('ses'),
      FixedDataModelElement('s4', b' msg=\'op=PAM:authentication acct="'),
      DelimitedDataModelElement('username', b'"'),
      FixedDataModelElement('s5', b'" exe="'),
      DelimitedDataModelElement('exec', b'"'),
      FixedDataModelElement('s6', b'" hostname='),
      DelimitedDataModelElement('clientname', b' '),
      FixedDataModelElement('s7', b' addr='),
      DelimitedDataModelElement('clientip', b' '),
      FixedDataModelElement('s8', b' terminal='),
      WhiteSpaceLimitedDataModelElement('terminal'),
      FixedDataModelElement('s9', b' res=success\'')
  ])

  typeBranches['USER_START'] = SequenceModelElement('userstart', [
      FixedDataModelElement('s0', b' pid='),
      DecimalIntegerValueModelElement('pid'),
      FixedDataModelElement('s1', b' uid='),
      DecimalIntegerValueModelElement('uid'),
      FixedDataModelElement('s2', b' auid='),
      DecimalIntegerValueModelElement('auid'),
      FixedDataModelElement('s3', b' ses='),
      DecimalIntegerValueModelElement('ses'),
      FixedDataModelElement('s4', b' msg=\'op=PAM:session_open acct="'),
      DelimitedDataModelElement('username', b'"'),
      FixedDataModelElement('s5', b'" exe="'),
      DelimitedDataModelElement('exec', b'"'),
      FixedDataModelElement('s6', b'" hostname='),
      DelimitedDataModelElement('clientname', b' '),
      FixedDataModelElement('s7', b' addr='),
      DelimitedDataModelElement('clientip', b' '),
      FixedDataModelElement('s8', b' terminal='),
      WhiteSpaceLimitedDataModelElement('terminal'),
      FixedDataModelElement('s9', b' res=success\'')
  ])

  typeBranches['USER_END'] = SequenceModelElement('userend', [
      FixedDataModelElement('s0', b' pid='),
      DecimalIntegerValueModelElement('pid'),
      FixedDataModelElement('s1', b' uid='),
      DecimalIntegerValueModelElement('uid'),
      FixedDataModelElement('s2', b' auid='),
      DecimalIntegerValueModelElement('auid'),
      FixedDataModelElement('s3', b' ses='),
      DecimalIntegerValueModelElement('ses'),
      FixedDataModelElement('s4', b' msg=\'op=PAM:session_close acct="'),
      DelimitedDataModelElement('username', b'"'),
      FixedDataModelElement('s5', b'" exe="'),
      DelimitedDataModelElement('exec', b'"'),
      FixedDataModelElement('s6', b'" hostname='),
      DelimitedDataModelElement('clientname', b' '),
      FixedDataModelElement('s7', b' addr='),
      DelimitedDataModelElement('clientip', b' '),
      FixedDataModelElement('s8', b' terminal='),
      WhiteSpaceLimitedDataModelElement('terminal'),
      FixedDataModelElement('s9', b' res=success\'')
  ])

  typeBranches['USER_ERR'] = SequenceModelElement('usererr', [
      FixedDataModelElement('s0', b' pid='),
      DecimalIntegerValueModelElement('pid'),
      FixedDataModelElement('s1', b' uid='),
      DecimalIntegerValueModelElement('uid'),
      FixedDataModelElement('s2', b' auid='),
      DecimalIntegerValueModelElement('auid'),
      FixedDataModelElement('s3', b' ses='),
      DecimalIntegerValueModelElement('ses'),
      FixedDataModelElement('s4', b' msg=\'op=PAM:bad_ident acct="?" exe="'),
      DelimitedDataModelElement('exec', b'"'),
      FixedDataModelElement('s5', b'" hostname='),
      DelimitedDataModelElement('clientname', b' '),
      FixedDataModelElement('s6', b' addr='),
      DelimitedDataModelElement('clientip', b' '),
      FixedDataModelElement('s7', b' terminal='),
      WhiteSpaceLimitedDataModelElement('terminal'),
      FixedDataModelElement('s8', b' res=failed\'')
  ])

  typeBranches['USER_LOGIN'] = SequenceModelElement('userlogin', [
      FixedDataModelElement('s0', b' pid='),
      DecimalIntegerValueModelElement('pid'),
      FixedDataModelElement('s1', b' uid='),
      DecimalIntegerValueModelElement('uid'),
      FixedDataModelElement('s2', b' auid='),
      DecimalIntegerValueModelElement('auid'),
      FixedDataModelElement('s3', b' ses='),
      DecimalIntegerValueModelElement('ses'),
      FixedDataModelElement('s4', b' msg=\'op=login '),
      FirstMatchModelElement('msgtype', [
          FixedDataModelElement('loginok', b'id=0'),
          SequenceModelElement('loginfail', [
              FixedDataModelElement('s0', b'acct='),
              ExecArgumentDataModelElement('account')
          ])]),
      FixedDataModelElement('s5', b' exe="'),
      DelimitedDataModelElement('exec', b'"'),
      FixedDataModelElement('s6', b'" hostname='),
      DelimitedDataModelElement('clientname', b' '),
      FixedDataModelElement('s7', b' addr='),
      DelimitedDataModelElement('clientip', b' '),
      FixedDataModelElement('s8', b' terminal='),
      WhiteSpaceLimitedDataModelElement('terminal'),
      FixedDataModelElement('s9', b' res='),
      pamStatusWordList,
      FixedDataModelElement('s10', b'\'')
  ])

  model = SequenceModelElement('audispd', [
      FixedDataModelElement('sname', b'audispd: '),
      FirstMatchModelElement('msg', [
          ElementValueBranchModelElement(
              'record', SequenceModelElement('preamble', [
                  FixedDataModelElement('s0', b'type='),
                  WhiteSpaceLimitedDataModelElement('type'),
                  FixedDataModelElement('s1', b' msg=audit('),
                  DecimalIntegerValueModelElement('time'),
                  FixedDataModelElement('s0', b'.'),
                  DecimalIntegerValueModelElement('ms'),
                  FixedDataModelElement('s1', b':'),
                  DecimalIntegerValueModelElement('seq'),
                  FixedDataModelElement('s2', b'):')
              ]),
              'type', typeBranches, defaultBranch=None),
          FixedDataModelElement('queue-full', b'queue is full - dropping event')
      ])
  ])
  return model
