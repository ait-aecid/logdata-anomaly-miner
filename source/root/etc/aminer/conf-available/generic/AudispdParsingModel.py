from aminer.parsing import AnyByteDataModelElement
from aminer.parsing import DecimalIntegerValueModelElement
from aminer.parsing import DelimitedDataModelElement
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

  class ExecArgumentDataModelElement:
    def __init__(self, id):
      self.id=id

    def getChildElements(self):
      return(None)

    def getMatchElement(self, path, matchContext):
      """Find the maximum number of bytes belonging to an exec
      argument.
      @return a match when at least two bytes were found including
      the delimiters."""
      data=matchContext.matchData
      matchLen=0
      matchValue=''
      if data[0] == '"':
        matchLen=data.find('"', 1)
        if matchLen==-1: return(None)
        matchValue=data[1:matchLen]
        matchLen+=1
      elif data.startswith('(null)'):
        matchLen=6
        matchValue=None
      else:
# Must be upper case hex encoded:
        nextValue=-1
        for dByte in data:
          dOrd=ord(dByte)
          if (dOrd>=0x30) and (dOrd<=0x39):
            dOrd-=0x30
          elif (dOrd>=0x41) and (dOrd<=0x46):
            dOrd-=0x37
          else:
            break
          if nextValue==-1: nextValue=(dOrd<<4)
          else:
            matchValue+=chr(nextValue|dOrd)
            nextValue=-1
          matchLen+=1
        if nextValue!=-1: return(None)

      matchData=data[:matchLen]
      matchContext.update(matchData)
      return(MatchElement("%s/%s" % (path, self.id),
          matchData, matchValue, None))

  pamStatusWordList=FixedWordlistDataModelElement('status', ['failed', 'success'])


# Define how to read the msgId sequence in all types of audit messages.
  msgIdPart=SequenceModelElement('msgid', [
      FixedDataModelElement('idpre', 'msg=audit('),
      DecimalIntegerValueModelElement('time'),
      FixedDataModelElement('s0', '.'),
      DecimalIntegerValueModelElement('ms'),
      FixedDataModelElement('s1', ':'),
      DecimalIntegerValueModelElement('seq'),
      FixedDataModelElement('s2', '):')])

  typeChildren=[]
  typeChildren.append(SequenceModelElement('bprmfcaps', [
      FixedDataModelElement('type', 'BPRM_FCAPS '),
      msgIdPart,
      FixedDataModelElement('s0', ' fver=0 fp='),
      HexStringModelElement('fp'),
      FixedDataModelElement('s1', ' fi='),
      HexStringModelElement('fi'),
      FixedDataModelElement('s2', ' fe='),
      HexStringModelElement('fe'),
      FixedDataModelElement('s3', ' old_pp='),
      HexStringModelElement('pp-old'),
      FixedDataModelElement('s4', ' old_pi='),
      HexStringModelElement('pi-old'),
      FixedDataModelElement('s5', ' old_pe='),
      HexStringModelElement('pe-old'),
      FixedDataModelElement('s6', ' new_pp='),
      HexStringModelElement('pp-new'),
      FixedDataModelElement('s7', ' new_pi='),
      HexStringModelElement('pi-new'),
      FixedDataModelElement('s8', ' new_pe='),
      HexStringModelElement('pe-new')
  ]))

  typeChildren.append(SequenceModelElement('conf-change', [
      FixedDataModelElement('type', 'CONFIG_CHANGE '),
      msgIdPart,
      FixedDataModelElement('s0', ' auid='),
      DecimalIntegerValueModelElement('auid'),
      FixedDataModelElement('s1', ' ses='),
      DecimalIntegerValueModelElement('ses'),
      FixedDataModelElement('s2', ' op="add rule" key=(null) list='),
      DecimalIntegerValueModelElement('list'),
      FixedDataModelElement('s3', ' res='),
      DecimalIntegerValueModelElement('result')
  ]))

  typeChildren.append(SequenceModelElement('credacq', [
      FixedDataModelElement('type', 'CRED_ACQ '),
      msgIdPart,
      FixedDataModelElement('s0', ' pid='),
      DecimalIntegerValueModelElement('pid'),
      FixedDataModelElement('s1', ' uid='),
      DecimalIntegerValueModelElement('uid'),
      FixedDataModelElement('s2', ' auid='),
      DecimalIntegerValueModelElement('auid'),
      FixedDataModelElement('s3', ' ses='),
      DecimalIntegerValueModelElement('ses'),
      FixedDataModelElement('s4', ' msg=\'op=PAM:setcred acct="'),
      DelimitedDataModelElement('username', '"'),
      FixedDataModelElement('s5', '" exe="'),
      DelimitedDataModelElement('exec', '"'),
      FixedDataModelElement('s6', '" hostname='),
      DelimitedDataModelElement('clientname', ' '),
      FixedDataModelElement('s7', ' addr='),
      DelimitedDataModelElement('clienip', ' '),
      FixedDataModelElement('s8', ' terminal='),
      WhiteSpaceLimitedDataModelElement('terminal'),
      FixedDataModelElement('s9', ' res=success\'')
]))

  typeChildren.append(SequenceModelElement('creddisp', [
      FixedDataModelElement('type', 'CRED_DISP '),
      msgIdPart,
      FixedDataModelElement('s0', ' pid='),
      DecimalIntegerValueModelElement('pid'),
      FixedDataModelElement('s1', ' uid='),
      DecimalIntegerValueModelElement('uid'),
      FixedDataModelElement('s2', ' auid='),
      DecimalIntegerValueModelElement('auid'),
      FixedDataModelElement('s3', ' ses='),
      DecimalIntegerValueModelElement('ses'),
      FixedDataModelElement('s4', ' msg=\'op=PAM:setcred acct="'),
      DelimitedDataModelElement('username', '"'),
      FixedDataModelElement('s5', '" exe="'),
      DelimitedDataModelElement('exec', '"'),
      FixedDataModelElement('s6', '" hostname='),
      DelimitedDataModelElement('clientname', ' '),
      FixedDataModelElement('s7', ' addr='),
      DelimitedDataModelElement('clienip', ' '),
      FixedDataModelElement('s8', ' terminal='),
      WhiteSpaceLimitedDataModelElement('terminal'),
      FixedDataModelElement('s9', ' res=success\'')
]))

  typeChildren.append(SequenceModelElement('creddisp', [
      FixedDataModelElement('type', 'CRED_REFR '),
      msgIdPart,
      FixedDataModelElement('s0', ' pid='),
      DecimalIntegerValueModelElement('pid'),
      FixedDataModelElement('s1', ' uid='),
      DecimalIntegerValueModelElement('uid'),
      FixedDataModelElement('s2', ' auid='),
      DecimalIntegerValueModelElement('auid'),
      FixedDataModelElement('s3', ' ses='),
      DecimalIntegerValueModelElement('ses'),
      FixedDataModelElement('s4', ' msg=\'op=PAM:setcred acct="root" exe="/usr/sbin/sshd" hostname='),
      IpAddressDataModelElement('clientname'),
      FixedDataModelElement('s5', ' addr='),
      IpAddressDataModelElement('clientip'),
      FixedDataModelElement('s6', ' terminal=ssh res=success\'')]))

  typeChildren.append(SequenceModelElement('cwd', [
      FixedDataModelElement('cwd', 'CWD '),
      msgIdPart,
      FixedDataModelElement('s0', '  cwd='),
      ExecArgumentDataModelElement('cwd')]))

  typeChildren.append(SequenceModelElement('eoe', [
      FixedDataModelElement('eoe', 'EOE '),
      msgIdPart]))

  execArgModel=SequenceModelElement('execarg', [
      FixedDataModelElement('s0', ' a'),
      DecimalIntegerValueModelElement('argn'),
      FixedDataModelElement('s1', '='),
      ExecArgumentDataModelElement('argval')])

  typeChildren.append(SequenceModelElement('execve', [
      FixedDataModelElement('execve', 'EXECVE '),
      msgIdPart,
      FixedDataModelElement('s0', ' argc='),
      DecimalIntegerValueModelElement('argc'),
      RepeatedElementDataModelElement('arg', execArgModel)]))

# This message differs on Ubuntu 32/64 bit variants.
  typeChildren.append(SequenceModelElement('login', [
      FixedDataModelElement('login', 'LOGIN '),
      msgIdPart,
      FixedDataModelElement('s0', ' pid='),
      DecimalIntegerValueModelElement('pid'),
      FixedDataModelElement('s1', ' uid='),
      DecimalIntegerValueModelElement('uid'),
      FixedWordlistDataModelElement('s2', [' old auid=', ' old-auid=']),
      DecimalIntegerValueModelElement('auid-old'),
      FixedWordlistDataModelElement('s3', [' new auid=', ' auid=']),
      DecimalIntegerValueModelElement('auid-new'),
      FixedWordlistDataModelElement('s4', [' old ses=', ' old-ses=']),
      DecimalIntegerValueModelElement('ses-old'),
      FixedWordlistDataModelElement('s5', [' new ses=', ' ses=']),
      DecimalIntegerValueModelElement('ses-new'),
      FixedDataModelElement('s6', ' res='),
      DecimalIntegerValueModelElement('result')]))

  inodeInfoModelElement=SequenceModelElement('inodeinfo', [
      FixedDataModelElement('s0', ' inode='),
      DecimalIntegerValueModelElement('inode'),
      FixedDataModelElement('s1', ' dev='),
# FIXME: dev element
      VariableByteDataModelElement('dev', '0123456789abcdef:'),
      FixedDataModelElement('s2', ' mode='),
# FIXME: is octal
      DecimalIntegerValueModelElement('mode'),
      FixedDataModelElement('s3', ' ouid='),
      DecimalIntegerValueModelElement('ouid'),
      FixedDataModelElement('s4', ' ogid='),
      DecimalIntegerValueModelElement('ogid'),
      FixedDataModelElement('s5', ' rdev='),
# FIXME: dev element
      VariableByteDataModelElement('rdev', '0123456789abcdef:'),
      FixedDataModelElement('s6', ' nametype=')])

  typeChildren.append(SequenceModelElement('conf-change', [
      FixedDataModelElement('type', 'NETFILTER_CFG '),
      msgIdPart,
      FixedDataModelElement('s0', ' table='),
      FixedWordlistDataModelElement('table', ['filter', 'mangle', 'nat']),
      FixedDataModelElement('s1', ' family='),
      DecimalIntegerValueModelElement('family'),
      FixedDataModelElement('s2', ' entries='),
      DecimalIntegerValueModelElement('entries')
  ])) 

  typeChildren.append(SequenceModelElement('path', [
      FixedDataModelElement('path', 'PATH '),
      msgIdPart,
      FixedDataModelElement('s0', ' item='),
      DecimalIntegerValueModelElement('item'),
      FixedDataModelElement('s1', ' name='),
      ExecArgumentDataModelElement('name'),
      FirstMatchModelElement('fsinfo', [
          inodeInfoModelElement,
          FixedDataModelElement('noinfo', ' nametype=')]),
      FixedWordlistDataModelElement('nametype', ['CREATE', 'DELETE', 'NORMAL', 'PARENT', 'UNKNOWN']),
]))

  typeChildren.append(SequenceModelElement('proctitle', [
      FixedDataModelElement('s0', 'PROCTITLE '),
      msgIdPart,
      FixedDataModelElement('s1', ' proctitle='),
      ExecArgumentDataModelElement('proctitle')]))

  typeChildren.append(SequenceModelElement('service', [
      FixedWordlistDataModelElement('nametype', ['SERVICE_START ', 'SERVICE_STOP ']),
      msgIdPart,
      FixedDataModelElement('s0', ' pid='),
      DecimalIntegerValueModelElement('pid'),
      FixedDataModelElement('s1', ' uid='),
      DecimalIntegerValueModelElement('uid'),
      FixedDataModelElement('s2', ' auid='),
      DecimalIntegerValueModelElement('auid'),
      FixedDataModelElement('s3', ' ses='),
      DecimalIntegerValueModelElement('ses'),
      FixedDataModelElement('s4', ' msg=\'unit='),
      DelimitedDataModelElement('unit', ' '),
      FixedDataModelElement('s5', ' comm="systemd" exe="'),
      DelimitedDataModelElement('exec', '"'),
      FixedDataModelElement('s6', '" hostname='),
      DelimitedDataModelElement('clientname', ' '),
      FixedDataModelElement('s7', ' addr='),
      DelimitedDataModelElement('clienip', ' '),
      FixedDataModelElement('s8', ' terminal='),
      WhiteSpaceLimitedDataModelElement('terminal'),
      FixedDataModelElement('s9', ' res='),
      pamStatusWordList,
      FixedDataModelElement('s10', '\'')
]))

  typeChildren.append(SequenceModelElement('sockaddr', [
      FixedDataModelElement('type', 'SOCKADDR '),
      msgIdPart,
      FixedDataModelElement('s0', ' saddr='),
      HexStringModelElement('sockaddr'),
  ]))

  typeChildren.append(SequenceModelElement('syscall', [
      FixedDataModelElement('syscall', 'SYSCALL '),
      msgIdPart,
      FixedDataModelElement('s0', ' arch='),
      HexStringModelElement('arch'),
      FixedDataModelElement('s1', ' syscall='),
      DecimalIntegerValueModelElement('syscall'),
      OptionalMatchModelElement('personality', SequenceModelElement('pseq', [
          FixedDataModelElement('s0', ' per='),
          DecimalIntegerValueModelElement('personality'),
      ])),
      FixedDataModelElement('s2', ' success='),
      FixedWordlistDataModelElement('succes', ['no', 'yes']),
      FixedDataModelElement('s3', ' exit='),
      DecimalIntegerValueModelElement('exit', valueSignType=DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL),
      FixedDataModelElement('s4', ' a0='),
      HexStringModelElement('arg0'),
      FixedDataModelElement('s5', ' a1='),
      HexStringModelElement('arg1'),
      FixedDataModelElement('s6', ' a2='),
      HexStringModelElement('arg2'),
      FixedDataModelElement('s7', ' a3='),
      HexStringModelElement('arg3'),
      FixedDataModelElement('s8', ' items='),
      DecimalIntegerValueModelElement('items'),
      FixedDataModelElement('s9', ' ppid='),
      DecimalIntegerValueModelElement('ppid'),
      FixedDataModelElement('s10', ' pid='),
      DecimalIntegerValueModelElement('pid'),
      FixedDataModelElement('s11', ' auid='),
      DecimalIntegerValueModelElement('auid'),
      FixedDataModelElement('s12', ' uid='),
      DecimalIntegerValueModelElement('uid'),
      FixedDataModelElement('s13', ' gid='),
      DecimalIntegerValueModelElement('gid'),
      FixedDataModelElement('s14', ' euid='),
      DecimalIntegerValueModelElement('euid'),
      FixedDataModelElement('s15', ' suid='),
      DecimalIntegerValueModelElement('suid'),
      FixedDataModelElement('s16', ' fsuid='),
      DecimalIntegerValueModelElement('fsuid'),
      FixedDataModelElement('s17', ' egid='),
      DecimalIntegerValueModelElement('egid'),
      FixedDataModelElement('s18', ' sgid='),
      DecimalIntegerValueModelElement('sgid'),
      FixedDataModelElement('s19', ' fsgid='),
      DecimalIntegerValueModelElement('fsgid'),
      FixedDataModelElement('s20', ' tty='),
      DelimitedDataModelElement('tty', ' '),
      FixedDataModelElement('s21', ' ses='),
      DecimalIntegerValueModelElement('sesid'),
      FixedDataModelElement('s22', ' comm='),
      ExecArgumentDataModelElement('command'),
      FixedDataModelElement('s23', ' exe="'),
      DelimitedDataModelElement('executable', '"'),
      FixedDataModelElement('s24', '" key='),
      AnyByteDataModelElement('key')
]))

# The UNKNOWN type is used then audispd does not know the type
# of the event, usually because the kernel is more recent than
# audispd, thus emiting yet unknown event types.
# * type=1327: procitle: see https://www.redhat.com/archives/linux-audit/2014-February/msg00047.html
  typeChildren.append(SequenceModelElement('unknown-proctitle', [
      FixedDataModelElement('type', 'UNKNOWN[1327] '),
      msgIdPart,
      FixedDataModelElement('s0', ' proctitle='),
      ExecArgumentDataModelElement('proctitle')
  ]))

  typeChildren.append(SequenceModelElement('useracct', [
      FixedDataModelElement('type', 'USER_ACCT '),
      msgIdPart,
      FixedDataModelElement('s0', ' pid='),
      DecimalIntegerValueModelElement('pid'),
      FixedDataModelElement('s1', ' uid='),
      DecimalIntegerValueModelElement('uid'),
      FixedDataModelElement('s2', ' auid='),
      DecimalIntegerValueModelElement('auid'),
      FixedDataModelElement('s3', ' ses='),
      DecimalIntegerValueModelElement('ses'),
      FixedDataModelElement('s4', ' msg=\'op=PAM:accounting acct="'),
      DelimitedDataModelElement('username', '"'),
      FixedDataModelElement('s5', '" exe="'),
      DelimitedDataModelElement('exec', '"'),
      FixedDataModelElement('s6', '" hostname='),
      DelimitedDataModelElement('clientname', ' '),
      FixedDataModelElement('s7', ' addr='),
      DelimitedDataModelElement('clienip', ' '),
      FixedDataModelElement('s8', ' terminal='),
      WhiteSpaceLimitedDataModelElement('terminal'),
      FixedDataModelElement('s9', ' res=success\'')
]))

  typeChildren.append(SequenceModelElement('userauth', [
      FixedDataModelElement('type', 'USER_AUTH '),
      msgIdPart,
      FixedDataModelElement('s0', ' pid='),
      DecimalIntegerValueModelElement('pid'),
      FixedDataModelElement('s1', ' uid='),
      DecimalIntegerValueModelElement('uid'),
      FixedDataModelElement('s2', ' auid='),
      DecimalIntegerValueModelElement('auid'),
      FixedDataModelElement('s3', ' ses='),
      DecimalIntegerValueModelElement('ses'),
      FixedDataModelElement('s4', ' msg=\'op=PAM:authentication acct="'),
      DelimitedDataModelElement('username', '"'),
      FixedDataModelElement('s5', '" exe="'),
      DelimitedDataModelElement('exec', '"'),
      FixedDataModelElement('s6', '" hostname='),
      DelimitedDataModelElement('clientname', ' '),
      FixedDataModelElement('s7', ' addr='),
      DelimitedDataModelElement('clienip', ' '),
      FixedDataModelElement('s8', ' terminal='),
      WhiteSpaceLimitedDataModelElement('terminal'),
      FixedDataModelElement('s9', ' res=success\'')
]))

  typeChildren.append(SequenceModelElement('userstart', [
      FixedDataModelElement('type', 'USER_START '),
      msgIdPart,
      FixedDataModelElement('s0', ' pid='),
      DecimalIntegerValueModelElement('pid'),
      FixedDataModelElement('s1', ' uid='),
      DecimalIntegerValueModelElement('uid'),
      FixedDataModelElement('s2', ' auid='),
      DecimalIntegerValueModelElement('auid'),
      FixedDataModelElement('s3', ' ses='),
      DecimalIntegerValueModelElement('ses'),
      FixedDataModelElement('s4', ' msg=\'op=PAM:session_open acct="'),
      DelimitedDataModelElement('username', '"'),
      FixedDataModelElement('s5', '" exe="'),
      DelimitedDataModelElement('exec', '"'),
      FixedDataModelElement('s6', '" hostname='),
      DelimitedDataModelElement('clientname', ' '),
      FixedDataModelElement('s7', ' addr='),
      DelimitedDataModelElement('clienip', ' '),
      FixedDataModelElement('s8', ' terminal='),
      WhiteSpaceLimitedDataModelElement('terminal'),
      FixedDataModelElement('s9', ' res=success\'')
]))

  typeChildren.append(SequenceModelElement('userend', [
      FixedDataModelElement('type', 'USER_END '),
      msgIdPart,
      FixedDataModelElement('s0', ' pid='),
      DecimalIntegerValueModelElement('pid'),
      FixedDataModelElement('s1', ' uid='),
      DecimalIntegerValueModelElement('uid'),
      FixedDataModelElement('s2', ' auid='),
      DecimalIntegerValueModelElement('auid'),
      FixedDataModelElement('s3', ' ses='),
      DecimalIntegerValueModelElement('ses'),
      FixedDataModelElement('s4', ' msg=\'op=PAM:session_close acct="'),
      DelimitedDataModelElement('username', '"'),
      FixedDataModelElement('s5', '" exe="'),
      DelimitedDataModelElement('exec', '"'),
      FixedDataModelElement('s6', '" hostname='),
      DelimitedDataModelElement('clientname', ' '),
      FixedDataModelElement('s7', ' addr='),
      DelimitedDataModelElement('clienip', ' '),
      FixedDataModelElement('s8', ' terminal='),
      WhiteSpaceLimitedDataModelElement('terminal'),
      FixedDataModelElement('s9', ' res=success\'')
]))

  typeChildren.append(SequenceModelElement('usererr', [
      FixedDataModelElement('type', 'USER_ERR '),
      msgIdPart,
      FixedDataModelElement('s0', ' pid='),
      DecimalIntegerValueModelElement('pid'),
      FixedDataModelElement('s1', ' uid='),
      DecimalIntegerValueModelElement('uid'),
      FixedDataModelElement('s2', ' auid='),
      DecimalIntegerValueModelElement('auid'),
      FixedDataModelElement('s3', ' ses='),
      DecimalIntegerValueModelElement('ses'),
      FixedDataModelElement('s4', ' msg=\'op=PAM:bad_ident acct="?" exe="'),
      DelimitedDataModelElement('exec', '"'),
      FixedDataModelElement('s5', '" hostname='),
      DelimitedDataModelElement('clientname', ' '),
      FixedDataModelElement('s6', ' addr='),
      DelimitedDataModelElement('clienip', ' '),
      FixedDataModelElement('s7', ' terminal='),
      WhiteSpaceLimitedDataModelElement('terminal'),
      FixedDataModelElement('s8', ' res=failed\'')
]))

  typeChildren.append(SequenceModelElement('userlogin', [
      FixedDataModelElement('type', 'USER_LOGIN '),
      msgIdPart,
      FixedDataModelElement('s0', ' pid='),
      DecimalIntegerValueModelElement('pid'),
      FixedDataModelElement('s1', ' uid='),
      DecimalIntegerValueModelElement('uid'),
      FixedDataModelElement('s2', ' auid='),
      DecimalIntegerValueModelElement('auid'),
      FixedDataModelElement('s3', ' ses='),
      DecimalIntegerValueModelElement('ses'),
      FixedDataModelElement('s4', ' msg=\'op=login '),
      FirstMatchModelElement('msgtype', [
          FixedDataModelElement('loginok', 'id=0'),
          SequenceModelElement('loginfail', [
              FixedDataModelElement('s0', 'acct='),
              ExecArgumentDataModelElement('account')
          ])]),
      FixedDataModelElement('s5', ' exe="'),
      DelimitedDataModelElement('exec', '"'),
      FixedDataModelElement('s6', '" hostname='),
      DelimitedDataModelElement('clientname', ' '),
      FixedDataModelElement('s7', ' addr='),
      DelimitedDataModelElement('clienip', ' '),
      FixedDataModelElement('s8', ' terminal='),
      WhiteSpaceLimitedDataModelElement('terminal'),
      FixedDataModelElement('s9', ' res='),
      pamStatusWordList,
      FixedDataModelElement('s10', '\'')
  ]))

  model=SequenceModelElement('audispd', [
      FixedDataModelElement('sname', 'audispd: '),
      FirstMatchModelElement('type', [
          SequenceModelElement('record', [
              FixedDataModelElement('s0', 'type='),
              FirstMatchModelElement('msgtype', typeChildren)]),
          FixedDataModelElement('queue-full', 'queue is full - dropping event')
      ])
  ])
  return(model)
