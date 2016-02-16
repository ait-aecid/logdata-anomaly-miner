from aminer.parsing import AnyByteDataModelElement
from aminer.parsing import DecimalIntegerValueModelElement
from aminer.parsing import DelimitedDataModelElement
from aminer.parsing import FirstMatchModelElement
from aminer.parsing import FixedDataModelElement
from aminer.parsing import FixedWordlistDataModelElement
from aminer.parsing import HexStringModelElement
from aminer.parsing import IpAddressDataModelElement
from aminer.parsing import MatchElement
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
      return(MatchElement.MatchElement("%s/%s" % (path, self.id),
          matchData, matchValue, None))


# Define how to read the msgId sequence in all types of audit messages.
  msgIdPart=SequenceModelElement.SequenceModelElement('msgid', [FixedDataModelElement.FixedDataModelElement('idpre', 'msg=audit('),
      DecimalIntegerValueModelElement.DecimalIntegerValueModelElement('time'),
      FixedDataModelElement.FixedDataModelElement('s0', '.'),
      DecimalIntegerValueModelElement.DecimalIntegerValueModelElement('ms'),
      FixedDataModelElement.FixedDataModelElement('s1', ':'),
      DecimalIntegerValueModelElement.DecimalIntegerValueModelElement('seq'),
      FixedDataModelElement.FixedDataModelElement('s2', '): ')])

  typeChildren=[]
  typeChildren.append(SequenceModelElement.SequenceModelElement('bprmfcaps', [FixedDataModelElement.FixedDataModelElement('type', 'BPRM_FCAPS '),
      msgIdPart,
      FixedDataModelElement.FixedDataModelElement('s0', 'fver=0 fp='),
      HexStringModelElement.HexStringModelElement('fp'),
      FixedDataModelElement.FixedDataModelElement('s1', ' fi='),
      HexStringModelElement.HexStringModelElement('fi'),
      FixedDataModelElement.FixedDataModelElement('s2', ' fe='),
      HexStringModelElement.HexStringModelElement('fe'),
      FixedDataModelElement.FixedDataModelElement('s3', ' old_pp='),
      HexStringModelElement.HexStringModelElement('pp-old'),
      FixedDataModelElement.FixedDataModelElement('s4', ' old_pi='),
      HexStringModelElement.HexStringModelElement('pi-old'),
      FixedDataModelElement.FixedDataModelElement('s5', ' old_pe='),
      HexStringModelElement.HexStringModelElement('pe-old'),
      FixedDataModelElement.FixedDataModelElement('s6', ' new_pp='),
      HexStringModelElement.HexStringModelElement('pp-new'),
      FixedDataModelElement.FixedDataModelElement('s7', ' new_pi='),
      HexStringModelElement.HexStringModelElement('pi-new'),
      FixedDataModelElement.FixedDataModelElement('s8', ' new_pe='),
      HexStringModelElement.HexStringModelElement('pe-new')
  ]))

  typeChildren.append(SequenceModelElement.SequenceModelElement('credacq', [FixedDataModelElement.FixedDataModelElement('type', 'CRED_ACQ '),
      msgIdPart,
      FixedDataModelElement.FixedDataModelElement('s0', 'pid='),
      DecimalIntegerValueModelElement.DecimalIntegerValueModelElement('pid'),
      FixedDataModelElement.FixedDataModelElement('s1', ' uid='),
      DecimalIntegerValueModelElement.DecimalIntegerValueModelElement('uid'),
      FixedDataModelElement.FixedDataModelElement('s2', ' auid='),
      DecimalIntegerValueModelElement.DecimalIntegerValueModelElement('auid'),
      FixedDataModelElement.FixedDataModelElement('s3', ' ses='),
      DecimalIntegerValueModelElement.DecimalIntegerValueModelElement('ses'),
      FixedDataModelElement.FixedDataModelElement('s4', ' msg=\'op=PAM:setcred acct="'),
      DelimitedDataModelElement.DelimitedDataModelElement('username', '"'),
      FixedDataModelElement.FixedDataModelElement('s5', '" exe="'),
      DelimitedDataModelElement.DelimitedDataModelElement('exec', '"'),
      FixedDataModelElement.FixedDataModelElement('s6', '" hostname='),
      DelimitedDataModelElement.DelimitedDataModelElement('clientname', ' '),
      FixedDataModelElement.FixedDataModelElement('s7', ' addr='),
      DelimitedDataModelElement.DelimitedDataModelElement('clienip', ' '),
      FixedDataModelElement.FixedDataModelElement('s8', ' terminal='),
      WhiteSpaceLimitedDataModelElement.WhiteSpaceLimitedDataModelElement('terminal'),
      FixedDataModelElement.FixedDataModelElement('s9', ' res=success\'')
]))

  typeChildren.append(SequenceModelElement.SequenceModelElement('creddisp', [FixedDataModelElement.FixedDataModelElement('type', 'CRED_DISP '),
      msgIdPart,
      FixedDataModelElement.FixedDataModelElement('s0', 'pid='),
      DecimalIntegerValueModelElement.DecimalIntegerValueModelElement('pid'),
      FixedDataModelElement.FixedDataModelElement('s1', ' uid='),
      DecimalIntegerValueModelElement.DecimalIntegerValueModelElement('uid'),
      FixedDataModelElement.FixedDataModelElement('s2', ' auid='),
      DecimalIntegerValueModelElement.DecimalIntegerValueModelElement('auid'),
      FixedDataModelElement.FixedDataModelElement('s3', ' ses='),
      DecimalIntegerValueModelElement.DecimalIntegerValueModelElement('ses'),
      FixedDataModelElement.FixedDataModelElement('s4', ' msg=\'op=PAM:setcred acct="'),
      DelimitedDataModelElement.DelimitedDataModelElement('username', '"'),
      FixedDataModelElement.FixedDataModelElement('s5', '" exe="'),
      DelimitedDataModelElement.DelimitedDataModelElement('exec', '"'),
      FixedDataModelElement.FixedDataModelElement('s6', '" hostname='),
      DelimitedDataModelElement.DelimitedDataModelElement('clientname', ' '),
      FixedDataModelElement.FixedDataModelElement('s7', ' addr='),
      DelimitedDataModelElement.DelimitedDataModelElement('clienip', ' '),
      FixedDataModelElement.FixedDataModelElement('s8', ' terminal='),
      WhiteSpaceLimitedDataModelElement.WhiteSpaceLimitedDataModelElement('terminal'),
      FixedDataModelElement.FixedDataModelElement('s9', ' res=success\'')
]))

  typeChildren.append(SequenceModelElement.SequenceModelElement('creddisp', [FixedDataModelElement.FixedDataModelElement('type', 'CRED_REFR '),
      msgIdPart,
      FixedDataModelElement.FixedDataModelElement('s0', 'pid='),
      DecimalIntegerValueModelElement.DecimalIntegerValueModelElement('pid'),
      FixedDataModelElement.FixedDataModelElement('s1', ' uid='),
      DecimalIntegerValueModelElement.DecimalIntegerValueModelElement('uid'),
      FixedDataModelElement.FixedDataModelElement('s2', ' auid='),
      DecimalIntegerValueModelElement.DecimalIntegerValueModelElement('auid'),
      FixedDataModelElement.FixedDataModelElement('s3', ' ses='),
      DecimalIntegerValueModelElement.DecimalIntegerValueModelElement('ses'),
      FixedDataModelElement.FixedDataModelElement('s4', ' msg=\'op=PAM:setcred acct="root" exe="/usr/sbin/sshd" hostname='),
      IpAddressDataModelElement.IpAddressDataModelElement('clientname'),
      FixedDataModelElement.FixedDataModelElement('s5', ' addr='),
      IpAddressDataModelElement.IpAddressDataModelElement('clientip'),
      FixedDataModelElement.FixedDataModelElement('s6', ' terminal=ssh res=success\'')]))

  typeChildren.append(SequenceModelElement.SequenceModelElement('cwd', [FixedDataModelElement.FixedDataModelElement('cwd', 'CWD '),
      msgIdPart,
      FixedDataModelElement.FixedDataModelElement('s0', ' cwd="'),
      DelimitedDataModelElement.DelimitedDataModelElement('cwd', '"'),
      FixedDataModelElement.FixedDataModelElement('s1', '"')]))

  typeChildren.append(SequenceModelElement.SequenceModelElement('eoe', [FixedDataModelElement.FixedDataModelElement('eoe', 'EOE '),
      msgIdPart]))

  execArgModel=SequenceModelElement.SequenceModelElement('execarg', [FixedDataModelElement.FixedDataModelElement('s0', ' a'),
      DecimalIntegerValueModelElement.DecimalIntegerValueModelElement('argn'),
      FixedDataModelElement.FixedDataModelElement('s1', '='),
      ExecArgumentDataModelElement('argval')])

  typeChildren.append(SequenceModelElement.SequenceModelElement('execve', [FixedDataModelElement.FixedDataModelElement('execve', 'EXECVE '),
      msgIdPart,
      FixedDataModelElement.FixedDataModelElement('s0', 'argc='),
      DecimalIntegerValueModelElement.DecimalIntegerValueModelElement('argc'),
      RepeatedElementDataModelElement.RepeatedElementDataModelElement('arg', execArgModel)]))

  typeChildren.append(SequenceModelElement.SequenceModelElement('login', [FixedDataModelElement.FixedDataModelElement('login', 'LOGIN '),
      msgIdPart,
      FixedDataModelElement.FixedDataModelElement('s0', 'pid='),
      DecimalIntegerValueModelElement.DecimalIntegerValueModelElement('pid'),
      FixedDataModelElement.FixedDataModelElement('s1', ' uid='),
      DecimalIntegerValueModelElement.DecimalIntegerValueModelElement('uid'),
      FixedDataModelElement.FixedDataModelElement('s2', ' old auid='),
      DecimalIntegerValueModelElement.DecimalIntegerValueModelElement('auid-old'),
      FixedDataModelElement.FixedDataModelElement('s3', ' new auid='),
      DecimalIntegerValueModelElement.DecimalIntegerValueModelElement('auid-new'),
      FixedDataModelElement.FixedDataModelElement('s4', ' old ses='),
      DecimalIntegerValueModelElement.DecimalIntegerValueModelElement('ses-old'),
      FixedDataModelElement.FixedDataModelElement('s5', ' new ses='),
      DecimalIntegerValueModelElement.DecimalIntegerValueModelElement('ses-new'),
      FixedDataModelElement.FixedDataModelElement('s6', ' res=1')]))

  inodeInfoModelElement=SequenceModelElement.SequenceModelElement('inodeinfo', [
      FixedDataModelElement.FixedDataModelElement('s0', ' inode='),
      DecimalIntegerValueModelElement.DecimalIntegerValueModelElement('inode'),
      FixedDataModelElement.FixedDataModelElement('s1', ' dev='),
# FIXME: dev element
      VariableByteDataModelElement.VariableByteDataModelElement('dev', '0123456789abcdef:'),
      FixedDataModelElement.FixedDataModelElement('s2', ' mode='),
# FIXME: is octal
      DecimalIntegerValueModelElement.DecimalIntegerValueModelElement('mode'),
      FixedDataModelElement.FixedDataModelElement('s3', ' ouid='),
      DecimalIntegerValueModelElement.DecimalIntegerValueModelElement('ouid'),
      FixedDataModelElement.FixedDataModelElement('s4', ' ogid='),
      DecimalIntegerValueModelElement.DecimalIntegerValueModelElement('ogid'),
      FixedDataModelElement.FixedDataModelElement('s5', ' rdev='),
# FIXME: dev element
      VariableByteDataModelElement.VariableByteDataModelElement('rdev', '0123456789abcdef:'),
      FixedDataModelElement.FixedDataModelElement('s6', ' nametype=')])

  typeChildren.append(SequenceModelElement.SequenceModelElement('path', [FixedDataModelElement.FixedDataModelElement('path', 'PATH '),
      msgIdPart,
      FixedDataModelElement.FixedDataModelElement('s0', 'item='),
      DecimalIntegerValueModelElement.DecimalIntegerValueModelElement('item'),
      FixedDataModelElement.FixedDataModelElement('s1', ' name='),
      ExecArgumentDataModelElement('name'),
      FirstMatchModelElement.FirstMatchModelElement('fsinfo', [
          inodeInfoModelElement,
          FixedDataModelElement.FixedDataModelElement('noinfo', ' nametype=')]),
      FixedWordlistDataModelElement.FixedWordlistDataModelElement('nametype', ['CREATE', 'DELETE', 'NORMAL', 'PARENT', 'UNKNOWN']),
]))

  typeChildren.append(SequenceModelElement.SequenceModelElement('syscall', [FixedDataModelElement.FixedDataModelElement('syscall', 'SYSCALL '),
      msgIdPart,
      FixedDataModelElement.FixedDataModelElement('s0', 'arch='),
      HexStringModelElement.HexStringModelElement('arch'),
      FixedDataModelElement.FixedDataModelElement('s1', ' syscall='),
      DecimalIntegerValueModelElement.DecimalIntegerValueModelElement('syscall'),
      FixedDataModelElement.FixedDataModelElement('s2', ' success='),
      FixedWordlistDataModelElement.FixedWordlistDataModelElement('succes', ['no', 'yes']),
      FixedDataModelElement.FixedDataModelElement('s3', ' exit='),
      DecimalIntegerValueModelElement.DecimalIntegerValueModelElement('exit', valueSignType=DecimalIntegerValueModelElement.DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL),
      FixedDataModelElement.FixedDataModelElement('s4', ' a0='),
      HexStringModelElement.HexStringModelElement('arg0'),
      FixedDataModelElement.FixedDataModelElement('s5', ' a1='),
      HexStringModelElement.HexStringModelElement('arg1'),
      FixedDataModelElement.FixedDataModelElement('s6', ' a2='),
      HexStringModelElement.HexStringModelElement('arg2'),
      FixedDataModelElement.FixedDataModelElement('s7', ' a3='),
      HexStringModelElement.HexStringModelElement('arg3'),
      FixedDataModelElement.FixedDataModelElement('s8', ' items='),
      DecimalIntegerValueModelElement.DecimalIntegerValueModelElement('items'),
      FixedDataModelElement.FixedDataModelElement('s9', ' ppid='),
      DecimalIntegerValueModelElement.DecimalIntegerValueModelElement('ppid'),
      FixedDataModelElement.FixedDataModelElement('s10', ' pid='),
      DecimalIntegerValueModelElement.DecimalIntegerValueModelElement('pid'),
      FixedDataModelElement.FixedDataModelElement('s11', ' auid='),
      DecimalIntegerValueModelElement.DecimalIntegerValueModelElement('auid'),
      FixedDataModelElement.FixedDataModelElement('s12', ' uid='),
      DecimalIntegerValueModelElement.DecimalIntegerValueModelElement('uid'),
      FixedDataModelElement.FixedDataModelElement('s13', ' gid='),
      DecimalIntegerValueModelElement.DecimalIntegerValueModelElement('gid'),
      FixedDataModelElement.FixedDataModelElement('s14', ' euid='),
      DecimalIntegerValueModelElement.DecimalIntegerValueModelElement('euid'),
      FixedDataModelElement.FixedDataModelElement('s15', ' suid='),
      DecimalIntegerValueModelElement.DecimalIntegerValueModelElement('suid'),
      FixedDataModelElement.FixedDataModelElement('s16', ' fsuid='),
      DecimalIntegerValueModelElement.DecimalIntegerValueModelElement('fsuid'),
      FixedDataModelElement.FixedDataModelElement('s17', ' egid='),
      DecimalIntegerValueModelElement.DecimalIntegerValueModelElement('egid'),
      FixedDataModelElement.FixedDataModelElement('s18', ' sgid='),
      DecimalIntegerValueModelElement.DecimalIntegerValueModelElement('sgid'),
      FixedDataModelElement.FixedDataModelElement('s19', ' fsgid='),
      DecimalIntegerValueModelElement.DecimalIntegerValueModelElement('fsgid'),
      FixedDataModelElement.FixedDataModelElement('s20', ' tty='),
      DelimitedDataModelElement.DelimitedDataModelElement('tty', ' '),
      FixedDataModelElement.FixedDataModelElement('s21', ' ses='),
      DecimalIntegerValueModelElement.DecimalIntegerValueModelElement('sesid'),
      FixedDataModelElement.FixedDataModelElement('s22', ' comm='),
      ExecArgumentDataModelElement('command'),
      FixedDataModelElement.FixedDataModelElement('s23', ' exe="'),
      DelimitedDataModelElement.DelimitedDataModelElement('executable', '"'),
      FixedDataModelElement.FixedDataModelElement('s24', '" key='),
      AnyByteDataModelElement.AnyByteDataModelElement('key')
]))

  typeChildren.append(SequenceModelElement.SequenceModelElement('useracct', [FixedDataModelElement.FixedDataModelElement('type', 'USER_ACCT '),
      msgIdPart,
      FixedDataModelElement.FixedDataModelElement('s0', 'pid='),
      DecimalIntegerValueModelElement.DecimalIntegerValueModelElement('pid'),
      FixedDataModelElement.FixedDataModelElement('s1', ' uid='),
      DecimalIntegerValueModelElement.DecimalIntegerValueModelElement('uid'),
      FixedDataModelElement.FixedDataModelElement('s2', ' auid='),
      DecimalIntegerValueModelElement.DecimalIntegerValueModelElement('auid'),
      FixedDataModelElement.FixedDataModelElement('s3', ' ses='),
      DecimalIntegerValueModelElement.DecimalIntegerValueModelElement('ses'),
      FixedDataModelElement.FixedDataModelElement('s4', ' msg=\'op=PAM:accounting acct="'),
      DelimitedDataModelElement.DelimitedDataModelElement('username', '"'),
      FixedDataModelElement.FixedDataModelElement('s5', '" exe="'),
      DelimitedDataModelElement.DelimitedDataModelElement('exec', '"'),
      FixedDataModelElement.FixedDataModelElement('s6', '" hostname='),
      DelimitedDataModelElement.DelimitedDataModelElement('clientname', ' '),
      FixedDataModelElement.FixedDataModelElement('s7', ' addr='),
      DelimitedDataModelElement.DelimitedDataModelElement('clienip', ' '),
      FixedDataModelElement.FixedDataModelElement('s8', ' terminal='),
      WhiteSpaceLimitedDataModelElement.WhiteSpaceLimitedDataModelElement('terminal'),
      FixedDataModelElement.FixedDataModelElement('s9', ' res=success\'')
]))

  typeChildren.append(SequenceModelElement.SequenceModelElement('userauth', [FixedDataModelElement.FixedDataModelElement('type', 'USER_AUTH '),
      msgIdPart,
      FixedDataModelElement.FixedDataModelElement('s0', 'pid='),
      DecimalIntegerValueModelElement.DecimalIntegerValueModelElement('pid'),
      FixedDataModelElement.FixedDataModelElement('s1', ' uid='),
      DecimalIntegerValueModelElement.DecimalIntegerValueModelElement('uid'),
      FixedDataModelElement.FixedDataModelElement('s2', ' auid='),
      DecimalIntegerValueModelElement.DecimalIntegerValueModelElement('auid'),
      FixedDataModelElement.FixedDataModelElement('s3', ' ses='),
      DecimalIntegerValueModelElement.DecimalIntegerValueModelElement('ses'),
      FixedDataModelElement.FixedDataModelElement('s4', ' msg=\'op=PAM:authentication acct="'),
      DelimitedDataModelElement.DelimitedDataModelElement('username', '"'),
      FixedDataModelElement.FixedDataModelElement('s5', '" exe="'),
      DelimitedDataModelElement.DelimitedDataModelElement('exec', '"'),
      FixedDataModelElement.FixedDataModelElement('s6', '" hostname='),
      DelimitedDataModelElement.DelimitedDataModelElement('clientname', ' '),
      FixedDataModelElement.FixedDataModelElement('s7', ' addr='),
      DelimitedDataModelElement.DelimitedDataModelElement('clienip', ' '),
      FixedDataModelElement.FixedDataModelElement('s8', ' terminal='),
      WhiteSpaceLimitedDataModelElement.WhiteSpaceLimitedDataModelElement('terminal'),
      FixedDataModelElement.FixedDataModelElement('s9', ' res=success\'')
]))


  typeChildren.append(SequenceModelElement.SequenceModelElement('userstart', [FixedDataModelElement.FixedDataModelElement('type', 'USER_START '),
      msgIdPart,
      FixedDataModelElement.FixedDataModelElement('s0', 'pid='),
      DecimalIntegerValueModelElement.DecimalIntegerValueModelElement('pid'),
      FixedDataModelElement.FixedDataModelElement('s1', ' uid='),
      DecimalIntegerValueModelElement.DecimalIntegerValueModelElement('uid'),
      FixedDataModelElement.FixedDataModelElement('s2', ' auid='),
      DecimalIntegerValueModelElement.DecimalIntegerValueModelElement('auid'),
      FixedDataModelElement.FixedDataModelElement('s3', ' ses='),
      DecimalIntegerValueModelElement.DecimalIntegerValueModelElement('ses'),
      FixedDataModelElement.FixedDataModelElement('s4', ' msg=\'op=PAM:session_open acct="'),
      DelimitedDataModelElement.DelimitedDataModelElement('username', '"'),
      FixedDataModelElement.FixedDataModelElement('s5', '" exe="'),
      DelimitedDataModelElement.DelimitedDataModelElement('exec', '"'),
      FixedDataModelElement.FixedDataModelElement('s6', '" hostname='),
      DelimitedDataModelElement.DelimitedDataModelElement('clientname', ' '),
      FixedDataModelElement.FixedDataModelElement('s7', ' addr='),
      DelimitedDataModelElement.DelimitedDataModelElement('clienip', ' '),
      FixedDataModelElement.FixedDataModelElement('s8', ' terminal='),
      WhiteSpaceLimitedDataModelElement.WhiteSpaceLimitedDataModelElement('terminal'),
      FixedDataModelElement.FixedDataModelElement('s9', ' res=success\'')
]))

  typeChildren.append(SequenceModelElement.SequenceModelElement('userend', [FixedDataModelElement.FixedDataModelElement('type', 'USER_END '),
      msgIdPart,
      FixedDataModelElement.FixedDataModelElement('s0', 'pid='),
      DecimalIntegerValueModelElement.DecimalIntegerValueModelElement('pid'),
      FixedDataModelElement.FixedDataModelElement('s1', ' uid='),
      DecimalIntegerValueModelElement.DecimalIntegerValueModelElement('uid'),
      FixedDataModelElement.FixedDataModelElement('s2', ' auid='),
      DecimalIntegerValueModelElement.DecimalIntegerValueModelElement('auid'),
      FixedDataModelElement.FixedDataModelElement('s3', ' ses='),
      DecimalIntegerValueModelElement.DecimalIntegerValueModelElement('ses'),
      FixedDataModelElement.FixedDataModelElement('s4', ' msg=\'op=PAM:session_close acct="'),
      DelimitedDataModelElement.DelimitedDataModelElement('username', '"'),
      FixedDataModelElement.FixedDataModelElement('s5', '" exe="'),
      DelimitedDataModelElement.DelimitedDataModelElement('exec', '"'),
      FixedDataModelElement.FixedDataModelElement('s6', '" hostname='),
      DelimitedDataModelElement.DelimitedDataModelElement('clientname', ' '),
      FixedDataModelElement.FixedDataModelElement('s7', ' addr='),
      DelimitedDataModelElement.DelimitedDataModelElement('clienip', ' '),
      FixedDataModelElement.FixedDataModelElement('s8', ' terminal='),
      WhiteSpaceLimitedDataModelElement.WhiteSpaceLimitedDataModelElement('terminal'),
      FixedDataModelElement.FixedDataModelElement('s9', ' res=success\'')
]))

  model=SequenceModelElement.SequenceModelElement('audispd', [FixedDataModelElement.FixedDataModelElement('sname', 'audispd: type='),
      FirstMatchModelElement.FirstMatchModelElement('msgtype', typeChildren)])
  return(model)
