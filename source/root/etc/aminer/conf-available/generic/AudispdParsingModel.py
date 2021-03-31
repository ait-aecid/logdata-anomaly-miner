"""This module contains functions and classes to create the parsing model."""

from aminer.parsing.AnyByteDataModelElement import AnyByteDataModelElement
from aminer.parsing.DecimalIntegerValueModelElement import DecimalIntegerValueModelElement
from aminer.parsing.DelimitedDataModelElement import DelimitedDataModelElement
from aminer.parsing.ElementValueBranchModelElement import ElementValueBranchModelElement
from aminer.parsing.FirstMatchModelElement import FirstMatchModelElement
from aminer.parsing.FixedDataModelElement import FixedDataModelElement
from aminer.parsing.FixedWordlistDataModelElement import FixedWordlistDataModelElement
from aminer.parsing.HexStringModelElement import HexStringModelElement
from aminer.parsing.IpAddressDataModelElement import IpAddressDataModelElement
from aminer.parsing.MatchElement import MatchElement
from aminer.parsing.OptionalMatchModelElement import OptionalMatchModelElement
from aminer.parsing.RepeatedElementDataModelElement import RepeatedElementDataModelElement
from aminer.parsing.SequenceModelElement import SequenceModelElement
from aminer.parsing.VariableByteDataModelElement import VariableByteDataModelElement
from aminer.parsing.WhiteSpaceLimitedDataModelElement import WhiteSpaceLimitedDataModelElement


def get_model():
    """Return a model to parse a audispd message logged via syslog after any standard logging preamble, e.g. from syslog."""

    class ExecArgumentDataModelElement():
        """This is a helper class for parsing the (encoded) exec argument strings found within audit logs."""

        def __init__(self, element_id):
            self.element_id = element_id

        @staticmethod
        def get_child_elements():
            """Get the children of this element (none)."""
            return None

        def get_match_element(self, path, match_context):
            """
            Find the maximum number of bytes belonging to an exec argument.
            @return a match when at least two bytes were found including the delimiters.
            """
            data = match_context.match_data
            match_len = 0
            match_value = b''
            if data[0] == ord(b'"'):
                match_len = data.find(b'"', 1)
                if match_len == -1:
                    return None
                match_value = data[1:match_len]
                match_len += 1
            elif data.startswith(b'(null)'):
                match_len = 6
                match_value = None
            else:
                # Must be upper case hex encoded:
                next_value = -1
                for d_byte in data:
                    if 0x30 <= d_byte <= 0x39:
                        d_byte -= 0x30
                    elif 0x41 <= d_byte <= 0x46:
                        d_byte -= 0x37
                    else:
                        break
                    if next_value == -1:
                        next_value = (d_byte << 4)
                    else:
                        match_value += bytearray(((next_value | d_byte),))
                        next_value = -1
                    match_len += 1
                if next_value != -1:
                    return None

            match_data = data[:match_len]
            match_context.update(match_data)
            return MatchElement("%s/%s" % (path, self.element_id), match_data, match_value, None)

    pam_status_word_list = FixedWordlistDataModelElement('status', [b'failed', b'success'])

    pid = b' pid='
    uid = b' uid='
    auid = b' auid='
    ses = b' ses='
    exe = b' exe="'
    hostname = b'" hostname='
    addr = b' addr='
    terminal = b' terminal='
    success = b' res=success\''
    res = b' res='
    exe1 = b'" exe="'

    type_branches = {
        'ADD_USER': SequenceModelElement('adduser', [
            FixedDataModelElement('s0', pid),
            DecimalIntegerValueModelElement('pid'),
            FixedDataModelElement('s1', uid),
            DecimalIntegerValueModelElement('uid'),
            FixedDataModelElement('s2', auid),
            DecimalIntegerValueModelElement('auid'),
            FixedDataModelElement('s3', ses),
            DecimalIntegerValueModelElement('ses'),
            FixedDataModelElement('s4', b' msg=\'op=adding user id='),
            DecimalIntegerValueModelElement('newuserid'),
            FixedDataModelElement('s5', exe),
            DelimitedDataModelElement('exec', b'"'),
            FixedDataModelElement('s6', hostname),
            DelimitedDataModelElement('clientname', b' '),
            FixedDataModelElement('s7', addr),
            DelimitedDataModelElement('clientip', b' '),
            FixedDataModelElement('s8', terminal),
            WhiteSpaceLimitedDataModelElement('terminal'),
            FixedDataModelElement('s9', success)
        ]),
        'BPRM_FCAPS': SequenceModelElement('bprmfcaps', [
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
        ]),
        'CONFIG_CHANGE': SequenceModelElement('conf-change', [
            FixedDataModelElement('s0', auid),
            DecimalIntegerValueModelElement('auid'),
            FixedDataModelElement('s1', ses),
            DecimalIntegerValueModelElement('ses'),
            FixedDataModelElement('s2', b' op="add rule" key=(null) list='),
            DecimalIntegerValueModelElement('list'),
            FixedDataModelElement('s3', res),
            DecimalIntegerValueModelElement('result')
        ]),
        'CRED_ACQ': SequenceModelElement('credacq', [
            FixedDataModelElement('s0', pid),
            DecimalIntegerValueModelElement('pid'),
            FixedDataModelElement('s1', uid),
            DecimalIntegerValueModelElement('uid'),
            FixedDataModelElement('s2', auid),
            DecimalIntegerValueModelElement('auid'),
            FixedDataModelElement('s3', ses),
            DecimalIntegerValueModelElement('ses'),
            FixedDataModelElement('s4', b' msg=\'op=PAM:setcred acct="'),
            DelimitedDataModelElement('username', b'"'),
            FixedDataModelElement('s5', exe1),
            DelimitedDataModelElement('exec', b'"'),
            FixedDataModelElement('s6', hostname),
            DelimitedDataModelElement('clientname', b' '),
            FixedDataModelElement('s7', addr),
            DelimitedDataModelElement('clientip', b' '),
            FixedDataModelElement('s8', terminal),
            WhiteSpaceLimitedDataModelElement('terminal'),
            FixedDataModelElement('s9', success)
        ]),
        'CRED_DISP': SequenceModelElement('creddisp', [
            FixedDataModelElement('s0', pid),
            DecimalIntegerValueModelElement('pid'),
            FixedDataModelElement('s1', uid),
            DecimalIntegerValueModelElement('uid'),
            FixedDataModelElement('s2', auid),
            DecimalIntegerValueModelElement('auid'),
            FixedDataModelElement('s3', ses),
            DecimalIntegerValueModelElement('ses'),
            FixedDataModelElement('s4', b' msg=\'op=PAM:setcred acct="'),
            DelimitedDataModelElement('username', b'"'),
            FixedDataModelElement('s5', exe1),
            DelimitedDataModelElement('exec', b'"'),
            FixedDataModelElement('s6', hostname),
            DelimitedDataModelElement('clientname', b' '),
            FixedDataModelElement('s7', addr),
            DelimitedDataModelElement('clientip', b' '),
            FixedDataModelElement('s8', terminal),
            WhiteSpaceLimitedDataModelElement('terminal'),
            FixedDataModelElement('s9', success)
        ]),
        'CRED_REFR': SequenceModelElement('creddisp', [
            FixedDataModelElement('s0', pid),
            DecimalIntegerValueModelElement('pid'),
            FixedDataModelElement('s1', uid),
            DecimalIntegerValueModelElement('uid'),
            FixedDataModelElement('s2', auid),
            DecimalIntegerValueModelElement('auid'),
            FixedDataModelElement('s3', ses),
            DecimalIntegerValueModelElement('ses'),
            FixedDataModelElement('s4', b' msg=\'op=PAM:setcred acct="root" exe="/usr/sbin/sshd" hostname='),
            IpAddressDataModelElement('clientname'),
            FixedDataModelElement('s5', addr),
            IpAddressDataModelElement('clientip'),
            FixedDataModelElement('s6', b' terminal=ssh res=success\'')
        ]),
        'CWD': SequenceModelElement('cwd', [
            FixedDataModelElement('s0', b'  cwd='),
            ExecArgumentDataModelElement('cwd')]),
        'EOE': OptionalMatchModelElement('eoe', FixedDataModelElement('s0', b''))
    }

    # We need a type branch here also, but there is no additional
    # data in EOE records after Ubuntu Trusty any more.
    exec_arg_model = SequenceModelElement('execarg', [
        FixedDataModelElement('s0', b' a'),
        DecimalIntegerValueModelElement('argn'),
        FixedDataModelElement('s1', b'='),
        ExecArgumentDataModelElement('argval')
    ])

    type_branches['EXECVE'] = SequenceModelElement('execve', [
        FixedDataModelElement('s0', b' argc='),
        DecimalIntegerValueModelElement('argc'),
        RepeatedElementDataModelElement('arg', exec_arg_model)
    ])

    type_branches['FD_PAIR'] = SequenceModelElement('fdpair', [
        FixedDataModelElement('s0', b' fd0='),
        DecimalIntegerValueModelElement('fd0'),
        FixedDataModelElement('s1', b' fd1='),
        DecimalIntegerValueModelElement('fd1')
    ])

    # This message differs on Ubuntu 32/64 bit variants.
    type_branches['LOGIN'] = SequenceModelElement('login', [
        FixedDataModelElement('s0', pid),
        DecimalIntegerValueModelElement('pid'),
        FixedDataModelElement('s1', uid),
        DecimalIntegerValueModelElement('uid'),
        FixedWordlistDataModelElement('s2', [b' old auid=', b' old-auid=']),
        DecimalIntegerValueModelElement('auid-old'),
        FixedWordlistDataModelElement('s3', [b' new auid=', auid]),
        DecimalIntegerValueModelElement('auid-new'),
        FixedWordlistDataModelElement('s4', [b' old ses=', b' old-ses=']),
        DecimalIntegerValueModelElement('ses-old'),
        FixedWordlistDataModelElement('s5', [b' new ses=', ses]),
        DecimalIntegerValueModelElement('ses-new'),
        FixedDataModelElement('s6', res),
        DecimalIntegerValueModelElement('result')
    ])

    inode_info_model_element = SequenceModelElement('inodeinfo', [
        FixedDataModelElement('s0', b' inode='),
        DecimalIntegerValueModelElement('inode'),
        FixedDataModelElement('s1', b' dev='),
        # A special major/minor device element could be better here.
        VariableByteDataModelElement('dev', b'0123456789abcdef:'),
        FixedDataModelElement('s2', b' mode='),
        # is octal
        DecimalIntegerValueModelElement('mode'),
        FixedDataModelElement('s3', b' ouid='),
        DecimalIntegerValueModelElement('ouid'),
        FixedDataModelElement('s4', b' ogid='),
        DecimalIntegerValueModelElement('ogid'),
        FixedDataModelElement('s5', b' rdev='),
        # A special major/minor device element could be better here (see above).
        VariableByteDataModelElement('rdev', b'0123456789abcdef:'),
        FixedDataModelElement('s6', b' nametype=')
    ])

    type_branches['NETFILTER_CFG'] = SequenceModelElement('conf-change', [
        FixedDataModelElement('s0', b' table='),
        FixedWordlistDataModelElement('table', [b'filter', b'mangle', b'nat']),
        FixedDataModelElement('s1', b' family='),
        DecimalIntegerValueModelElement('family'),
        FixedDataModelElement('s2', b' entries='),
        DecimalIntegerValueModelElement('entries')
    ])

    type_branches['OBJ_PID'] = SequenceModelElement('objpid', [
        FixedDataModelElement('s0', b' opid='),
        DecimalIntegerValueModelElement('opid'),
        FixedDataModelElement('s1', b' oauid='),
        DecimalIntegerValueModelElement('oauid', value_sign_type=DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL),
        FixedDataModelElement('s2', b' ouid='),
        DecimalIntegerValueModelElement('ouid'),
        FixedDataModelElement('s3', b' oses='),
        DecimalIntegerValueModelElement('oses', value_sign_type=DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL),
        FixedDataModelElement('s4', b' ocomm='),
        ExecArgumentDataModelElement('ocomm')
    ])

    type_branches['PATH'] = SequenceModelElement('path', [
        FixedDataModelElement('s0', b' item='),
        DecimalIntegerValueModelElement('item'),
        FixedDataModelElement('s1', b' name='),
        ExecArgumentDataModelElement('name'),
        FirstMatchModelElement('fsinfo', [
            inode_info_model_element,
            FixedDataModelElement('noinfo', b' nametype=')]),
        FixedWordlistDataModelElement('nametype', [b'CREATE', b'DELETE', b'NORMAL', b'PARENT', b'UNKNOWN'])
    ])

    type_branches['PROCTITLE'] = SequenceModelElement('proctitle', [
        FixedDataModelElement('s1', b' proctitle='),
        ExecArgumentDataModelElement('proctitle')])

    type_branches['SERVICE_START'] = SequenceModelElement('service', [
        FixedDataModelElement('s0', pid),
        DecimalIntegerValueModelElement('pid'),
        FixedDataModelElement('s1', uid),
        DecimalIntegerValueModelElement('uid'),
        FixedDataModelElement('s2', auid),
        DecimalIntegerValueModelElement('auid'),
        FixedDataModelElement('s3', ses),
        DecimalIntegerValueModelElement('ses'),
        FixedDataModelElement('s4', b' msg=\'unit='),
        DelimitedDataModelElement('unit', b' '),
        FixedDataModelElement('s5', b' comm="systemd" exe="'),
        DelimitedDataModelElement('exec', b'"'),
        FixedDataModelElement('s6', hostname),
        DelimitedDataModelElement('clientname', b' '),
        FixedDataModelElement('s7', addr),
        DelimitedDataModelElement('clientip', b' '),
        FixedDataModelElement('s8', terminal),
        WhiteSpaceLimitedDataModelElement('terminal'),
        FixedDataModelElement('s9', res),
        pam_status_word_list,
        FixedDataModelElement('s10', b'\'')
    ])

    type_branches['SERVICE_STOP'] = type_branches['SERVICE_START']

    type_branches['SOCKADDR'] = SequenceModelElement('sockaddr', [
        FixedDataModelElement('s0', b' saddr='),
        HexStringModelElement('sockaddr', upper_case=True)
    ])

    type_branches['SYSCALL'] = SequenceModelElement('syscall', [
        FixedDataModelElement('s0', b' arch='),
        HexStringModelElement('arch'),
        FixedDataModelElement('s1', b' syscall='),
        DecimalIntegerValueModelElement('syscall'),
        OptionalMatchModelElement(
            'personality', SequenceModelElement('pseq', [
                FixedDataModelElement('s0', b' per='),
                DecimalIntegerValueModelElement('personality')
            ])),
        OptionalMatchModelElement('result', SequenceModelElement('rseq', [
            FixedDataModelElement('s2', b' success='),
            FixedWordlistDataModelElement('succes', [b'no', b'yes']),
            FixedDataModelElement('s3', b' exit='),
            DecimalIntegerValueModelElement('exit', value_sign_type=DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL)
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
        FixedDataModelElement('s10', pid),
        DecimalIntegerValueModelElement('pid'),
        FixedDataModelElement('s11', auid),
        DecimalIntegerValueModelElement('auid'),
        FixedDataModelElement('s12', uid),
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
        FixedDataModelElement('s21', ses),
        DecimalIntegerValueModelElement('sesid'),
        FixedDataModelElement('s22', b' comm='),
        ExecArgumentDataModelElement('command'),
        FixedDataModelElement('s23', exe),
        DelimitedDataModelElement('executable', b'"'),
        FixedDataModelElement('s24', b'" key='),
        AnyByteDataModelElement('key')
    ])

    # The UNKNOWN type is used then audispd does not know the type of the event, usually because the kernel is more recent than
    # audispd, thus emiting yet unknown event types.
    # * type=1327: procitle: see https://www.redhat.com/archives/linux-audit/2014-February/msg00047.html
    type_branches['UNKNOWN[1327]'] = SequenceModelElement('unknown-proctitle', [
        FixedDataModelElement('s0', b' proctitle='),
        ExecArgumentDataModelElement('proctitle')
    ])

    type_branches['USER_ACCT'] = SequenceModelElement('useracct', [
        FixedDataModelElement('s0', pid),
        DecimalIntegerValueModelElement('pid'),
        FixedDataModelElement('s1', uid),
        DecimalIntegerValueModelElement('uid'),
        FixedDataModelElement('s2', auid),
        DecimalIntegerValueModelElement('auid'),
        FixedDataModelElement('s3', ses),
        DecimalIntegerValueModelElement('ses'),
        FixedDataModelElement('s4', b' msg=\'op=PAM:accounting acct="'),
        DelimitedDataModelElement('username', b'"'),
        FixedDataModelElement('s5', exe1),
        DelimitedDataModelElement('exec', b'"'),
        FixedDataModelElement('s6', hostname),
        DelimitedDataModelElement('clientname', b' '),
        FixedDataModelElement('s7', addr),
        DelimitedDataModelElement('clientip', b' '),
        FixedDataModelElement('s8', terminal),
        WhiteSpaceLimitedDataModelElement('terminal'),
        FixedDataModelElement('s9', success)
    ])

    type_branches['USER_AUTH'] = SequenceModelElement('userauth', [
        FixedDataModelElement('s0', pid),
        DecimalIntegerValueModelElement('pid'),
        FixedDataModelElement('s1', uid),
        DecimalIntegerValueModelElement('uid'),
        FixedDataModelElement('s2', auid),
        DecimalIntegerValueModelElement('auid'),
        FixedDataModelElement('s3', ses),
        DecimalIntegerValueModelElement('ses'),
        FixedDataModelElement('s4', b' msg=\'op=PAM:authentication acct="'),
        DelimitedDataModelElement('username', b'"'),
        FixedDataModelElement('s5', exe1),
        DelimitedDataModelElement('exec', b'"'),
        FixedDataModelElement('s6', hostname),
        DelimitedDataModelElement('clientname', b' '),
        FixedDataModelElement('s7', addr),
        DelimitedDataModelElement('clientip', b' '),
        FixedDataModelElement('s8', terminal),
        WhiteSpaceLimitedDataModelElement('terminal'),
        FixedDataModelElement('s9', success)
    ])

    type_branches['USER_START'] = SequenceModelElement('userstart', [
        FixedDataModelElement('s0', pid),
        DecimalIntegerValueModelElement('pid'),
        FixedDataModelElement('s1', uid),
        DecimalIntegerValueModelElement('uid'),
        FixedDataModelElement('s2', auid),
        DecimalIntegerValueModelElement('auid'),
        FixedDataModelElement('s3', ses),
        DecimalIntegerValueModelElement('ses'),
        FixedDataModelElement('s4', b' msg=\'op=PAM:session_open acct="'),
        DelimitedDataModelElement('username', b'"'),
        FixedDataModelElement('s5', exe1),
        DelimitedDataModelElement('exec', b'"'),
        FixedDataModelElement('s6', hostname),
        DelimitedDataModelElement('clientname', b' '),
        FixedDataModelElement('s7', addr),
        DelimitedDataModelElement('clientip', b' '),
        FixedDataModelElement('s8', terminal),
        WhiteSpaceLimitedDataModelElement('terminal'),
        FixedDataModelElement('s9', success)])

    type_branches['USER_END'] = SequenceModelElement('userend', [
        FixedDataModelElement('s0', pid),
        DecimalIntegerValueModelElement('pid'),
        FixedDataModelElement('s1', uid),
        DecimalIntegerValueModelElement('uid'),
        FixedDataModelElement('s2', auid),
        DecimalIntegerValueModelElement('auid'),
        FixedDataModelElement('s3', ses),
        DecimalIntegerValueModelElement('ses'),
        FixedDataModelElement('s4', b' msg=\'op=PAM:session_close acct="'),
        DelimitedDataModelElement('username', b'"'),
        FixedDataModelElement('s5', exe1),
        DelimitedDataModelElement('exec', b'"'),
        FixedDataModelElement('s6', hostname),
        DelimitedDataModelElement('clientname', b' '),
        FixedDataModelElement('s7', addr),
        DelimitedDataModelElement('clientip', b' '),
        FixedDataModelElement('s8', terminal),
        WhiteSpaceLimitedDataModelElement('terminal'),
        FixedDataModelElement('s9', success)])

    type_branches['USER_ERR'] = SequenceModelElement('usererr', [
        FixedDataModelElement('s0', pid),
        DecimalIntegerValueModelElement('pid'),
        FixedDataModelElement('s1', uid),
        DecimalIntegerValueModelElement('uid'),
        FixedDataModelElement('s2', auid),
        DecimalIntegerValueModelElement('auid'),
        FixedDataModelElement('s3', ses),
        DecimalIntegerValueModelElement('ses'),
        FixedDataModelElement('s4', b' msg=\'op=PAM:bad_ident acct="?" exe="'),
        DelimitedDataModelElement('exec', b'"'),
        FixedDataModelElement('s5', hostname),
        DelimitedDataModelElement('clientname', b' '),
        FixedDataModelElement('s6', addr),
        DelimitedDataModelElement('clientip', b' '),
        FixedDataModelElement('s7', terminal),
        WhiteSpaceLimitedDataModelElement('terminal'),
        FixedDataModelElement('s8', b' res=failed\'')])

    type_branches['USER_LOGIN'] = SequenceModelElement('userlogin', [
        FixedDataModelElement('s0', pid),
        DecimalIntegerValueModelElement('pid'),
        FixedDataModelElement('s1', uid),
        DecimalIntegerValueModelElement('uid'),
        FixedDataModelElement('s2', auid),
        DecimalIntegerValueModelElement('auid'),
        FixedDataModelElement('s3', ses),
        DecimalIntegerValueModelElement('ses'),
        FixedDataModelElement('s4', b' msg=\'op=login '),
        FirstMatchModelElement('msgtype', [
            FixedDataModelElement('loginok', b'id=0'),
            SequenceModelElement('loginfail', [
                FixedDataModelElement('s0', b'acct='),
                ExecArgumentDataModelElement('account')])
        ]),
        FixedDataModelElement('s5', exe),
        DelimitedDataModelElement('exec', b'"'),
        FixedDataModelElement('s6', hostname),
        DelimitedDataModelElement('clientname', b' '),
        FixedDataModelElement('s7', addr),
        DelimitedDataModelElement('clientip', b' '),
        FixedDataModelElement('s8', terminal),
        WhiteSpaceLimitedDataModelElement('terminal'),
        FixedDataModelElement('s9', res),
        pam_status_word_list,
        FixedDataModelElement('s10', b'\'')
    ])

    model = SequenceModelElement('audispd', [
        FixedDataModelElement('sname', b'audispd: '),
        FirstMatchModelElement('msg', [
            ElementValueBranchModelElement('record', SequenceModelElement('preamble', [
                FixedDataModelElement('s0', b'type='),
                WhiteSpaceLimitedDataModelElement('type'),
                FixedDataModelElement('s1', b' msg=audit('),
                DecimalIntegerValueModelElement('time'),
                FixedDataModelElement('s0', b'.'),
                DecimalIntegerValueModelElement('ms'),
                FixedDataModelElement('s1', b':'),
                DecimalIntegerValueModelElement('seq'),
                FixedDataModelElement('s2', b'):')
            ]), 'type', type_branches, default_branch=None),
            FixedDataModelElement('queue-full', b'queue is full - dropping event')
        ])
    ])
    return model
