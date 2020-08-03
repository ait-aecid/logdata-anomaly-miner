"""This module defines a generated parser model."""

from aminer.parsing import AnyByteDataModelElement
from aminer.parsing import Base64StringModelElement
from aminer.parsing import DateTimeModelElement
from aminer.parsing import DecimalFloatValueModelElement
from aminer.parsing import DecimalIntegerValueModelElement
from aminer.parsing import DelimitedDataModelElement
from aminer.parsing import FirstMatchModelElement
from aminer.parsing import FixedDataModelElement
from aminer.parsing import FixedWordlistDataModelElement
from aminer.parsing import HexStringModelElement
from aminer.parsing import IpAddressDataModelElement
from aminer.parsing import OptionalMatchModelElement
from aminer.parsing import SequenceModelElement
from aminer.parsing import VariableByteDataModelElement

def getModel():
	dict = b'!"#$%&\'()*+,-./0123456789:;<>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ\\^_`abcdefghijklmnopqrstuvwxyz{|}~=[]'

    seq = [FixedDataModelElement('audit_str', b'audit('),
        DateTimeModelElement('time', b'%s.%f'),
        FixedDataModelElement('colon_str', b':'),
        DecimalIntegerValueModelElement('id'),
        FixedDataModelElement('pid_str', b'): pid='),
        VariableByteDataModelElement('pid', dict),
        FixedDataModelElement('uid_str', b' uid='),
        VariableByteDataModelElement('uid', dict),
        FixedDataModelElement('auid_str', b' auid='),
        VariableByteDataModelElement('auid', dict),
        FixedDataModelElement('ses_str', b' ses='),
        VariableByteDataModelElement('ses', dict),
        FixedDataModelElement('msg2_str', b' msg='),
        VariableByteDataModelElement('msg2', dict),
        FirstMatchModelElement('fm', [
            SequenceModelElement('acct', [
                FixedDataModelElement('acct_str', b' acct='),
                VariableByteDataModelElement('acct', dict)]),
            SequenceModelElement('comm', [
                FixedDataModelElement('comm_str', b' comm='),
                VariableByteDataModelElement('comm', dict)]),
            SequenceModelElement('cmd', [
                FixedDataModelElement('cmd_str', b' cmd='),
                VariableByteDataModelElement('cmd', dict)])]),
        OptionalMatchModelElement('opt',
            SequenceModelElement('opt_seq', [
                FixedDataModelElement('exe_str', b' exe='),
                VariableByteDataModelElement('exe', dict),
                FixedDataModelElement('hostname_str', b' hostname='),
                VariableByteDataModelElement('hostname', dict),
                FixedDataModelElement('addr_str', b' addr='),
                VariableByteDataModelElement('addr', dict)])),
        FixedDataModelElement('terminal_str', b' terminal='),
        VariableByteDataModelElement('terminal', dict),
        FixedDataModelElement('res_str', b' res='),
        VariableByteDataModelElement('res', dict)]

	model = SequenceModelElement('model', [
		FixedDataModelElement('type_str', b'type='),
		FirstMatchModelElement('type', [
			SequenceModelElement('execve', [
				FixedDataModelElement('execve_str', b'EXECVE msg=audit('),
				DateTimeModelElement('time', b'%s.%f'),
				FixedDataModelElement('colon_str', b':'),
				DecimalIntegerValueModelElement('id'),
				FixedDataModelElement('argc_str', b'): argc='),
				DecimalIntegerValueModelElement('argc', value_sign_type = DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL),
				FixedDataModelElement('a0_str', b' a0='),
				VariableByteDataModelElement('a0', dict),
				OptionalMatchModelElement('opt1', 
					SequenceModelElement('seq1', [
						FixedDataModelElement('a1_str', b' a1='),
						VariableByteDataModelElement('a1', dict),
						OptionalMatchModelElement('opt2', 
							SequenceModelElement('seq2', [
								FixedDataModelElement('a2_str', b' a2='),
								VariableByteDataModelElement('a2', dict),
								OptionalMatchModelElement('opt3', 
									SequenceModelElement('seq3', [
										FixedDataModelElement('a3_str', b' a3='),
										VariableByteDataModelElement('a3', dict),
										OptionalMatchModelElement('opt4', 
											SequenceModelElement('seq4', [
												FixedDataModelElement('a4_str', b' a4='),
												VariableByteDataModelElement('a4', dict)])),
												OptionalMatchModelElement('opt5', 
													SequenceModelElement('seq5', [
														FixedDataModelElement('a5_str', b' a5='),
														VariableByteDataModelElement('a5', dict)])),
														OptionalMatchModelElement('opt6', 
															SequenceModelElement('seq6', [
																FixedDataModelElement('a6_str', b' a6='),
																VariableByteDataModelElement('a6', dict)])),
																OptionalMatchModelElement('opt7', 
																	SequenceModelElement('seq7', [
																		FixedDataModelElement('a7_str', b' a7='),
																		VariableByteDataModelElement('a7', dict)])),
																		OptionalMatchModelElement('opt8', 
																			SequenceModelElement('seq8', [
																				FixedDataModelElement('a8_str', b' a8='),
																				VariableByteDataModelElement('a8', dict)])),
																				OptionalMatchModelElement('opt9', 
																					SequenceModelElement('seq9', [
																						FixedDataModelElement('a9_str', b' a9='),
																						VariableByteDataModelElement('a9', dict)])),
																						OptionalMatchModelElement('opt10', 
																							SequenceModelElement('seq10', [
																								FixedDataModelElement('a10_str', b' a10='),
																								VariableByteDataModelElement('a10', dict)])),
																								OptionalMatchModelElement('opt11', 
																									SequenceModelElement('seq11', [
																										FixedDataModelElement('a11_str', b' a11='),
																										VariableByteDataModelElement('a11', dict)])),
																										OptionalMatchModelElement('opt12', 
																											SequenceModelElement('seq12', [
																												FixedDataModelElement('a12_str', b' a12='),
																												VariableByteDataModelElement('a12', dict)])),
																												OptionalMatchModelElement('opt13', 
																													SequenceModelElement('seq13', [
																														FixedDataModelElement('a13_str', b' a13='),
																														VariableByteDataModelElement('a13', dict)])),
																														OptionalMatchModelElement('opt14', 
																															SequenceModelElement('seq14', [
																																FixedDataModelElement('a14_str', b' a14='),
																																VariableByteDataModelElement('a14', dict)])),]))]))]))]),
			SequenceModelElement('proctitle', [
				FixedDataModelElement('type_str', b'PROCTITLE msg=audit('),
				DateTimeModelElement('time', b'%s.%f'),
				FixedDataModelElement('colon_str', b':'),
				DecimalIntegerValueModelElement('id'),
				FixedDataModelElement('proctitle_str', b'): proctitle='),
				VariableByteDataModelElement('proctitle', dict)]),
			SequenceModelElement('syscall', [
				FixedDataModelElement('msg_str', b'SYSCALL msg=audit('),
				DateTimeModelElement('time', b'%s.%f'),
				FixedDataModelElement('colon_str', b':'),
				DecimalIntegerValueModelElement('id'),
				FixedDataModelElement('arch_str', b'): arch='),
				VariableByteDataModelElement('arch', dict),
				FixedDataModelElement('syscall_str', b' syscall='),
				DecimalIntegerValueModelElement('syscall', value_sign_type = DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL),
				FixedDataModelElement('success_str', b' success='),
				VariableByteDataModelElement('success', dict),
				FixedDataModelElement('exit_str', b' exit='),
				VariableByteDataModelElement('exit', dict),
				FixedDataModelElement('a0_str', b' a0='),
				VariableByteDataModelElement('a0', dict),
				FixedDataModelElement('a1_str', b' a1='),
				VariableByteDataModelElement('a1', dict),
				FixedDataModelElement('a2_str', b' a2='),
				VariableByteDataModelElement('a2', dict),
				FixedDataModelElement('a3_str', b' a3='),
				VariableByteDataModelElement('a3', dict),
				FixedDataModelElement('items_str', b' items='),
				VariableByteDataModelElement('items', dict),
				FixedDataModelElement('ppid_str', b' ppid='),
				VariableByteDataModelElement('ppid', dict),
				FixedDataModelElement('pid_str', b' pid='),
				VariableByteDataModelElement('pid', dict),
				FixedDataModelElement('auid_str', b' auid='),
				VariableByteDataModelElement('auid', dict),
				FixedDataModelElement('uid_str', b' uid='),
				VariableByteDataModelElement('uid', dict),
				FixedDataModelElement('gid_str', b' gid='),
				VariableByteDataModelElement('gid', dict),
				FixedDataModelElement('euid_str', b' euid='),
				VariableByteDataModelElement('euid', dict),
				FixedDataModelElement('suid_str', b' suid='),
				VariableByteDataModelElement('suid', dict),
				FixedDataModelElement('fsuid_str', b' fsuid='),
				VariableByteDataModelElement('fsuid', dict),
				FixedDataModelElement('egid_str', b' egid='),
				VariableByteDataModelElement('egid', dict),
				FixedDataModelElement('sgid_str', b' sgid='),
				VariableByteDataModelElement('sgid', dict),
				FixedDataModelElement('fsgid_str', b' fsgid='),
				VariableByteDataModelElement('fsgid', dict),
				FixedDataModelElement('tty_str', b' tty='),
				VariableByteDataModelElement('tty', dict),
				FixedDataModelElement('ses_str', b' ses='),
				VariableByteDataModelElement('ses', dict),
				FixedDataModelElement('comm_str', b' comm='),
				VariableByteDataModelElement('comm', dict),
				FixedDataModelElement('exe_str', b' exe='),
				VariableByteDataModelElement('exe', dict),
				FixedDataModelElement('key_str', b' key='),
				VariableByteDataModelElement('key', dict)]),
			SequenceModelElement('path', [
				FixedDataModelElement('msg_str', b'PATH msg=audit('),
				DateTimeModelElement('time', b'%s.%f'),
				FixedDataModelElement('colon_str', b':'),
				DecimalIntegerValueModelElement('id'),
				FixedDataModelElement('item_str', b'): item='),
				DecimalIntegerValueModelElement('item', value_sign_type = DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL),
				FixedDataModelElement('name_str', b' name='),
				VariableByteDataModelElement('name', dict),
				FirstMatchModelElement('path', [
					SequenceModelElement('nametype', [
						FixedDataModelElement('nametype_str', b' nametype='),
						VariableByteDataModelElement('nametype', dict)]),
					SequenceModelElement('inode', [
						FixedDataModelElement('inode_str', b' inode='),
						DecimalIntegerValueModelElement('inode', value_sign_type = DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL),
						FixedDataModelElement('dev_str', b' dev='),
						VariableByteDataModelElement('dev', dict),
						FixedDataModelElement('mode_str', b' mode='),
						VariableByteDataModelElement('mode', dict),
						FixedDataModelElement('ouid_str', b' ouid='),
						VariableByteDataModelElement('ouid', dict),
						FixedDataModelElement('ogid_str', b' ogid='),
						VariableByteDataModelElement('ogid', dict),
						FixedDataModelElement('rdev_str', b' rdev='),
						VariableByteDataModelElement('rdev', dict),
						FixedDataModelElement('nametype_str', b' nametype='),
						VariableByteDataModelElement('nametype', dict)])])]),
			SequenceModelElement('login', [
				FixedDataModelElement('msg1_str', b'LOGIN msg=audit('),
				DateTimeModelElement('time', b'%s.%f'),
				FixedDataModelElement('colon_str', b':'),
				DecimalIntegerValueModelElement('id'),
				FixedDataModelElement('pid_str', b'): pid='),
				VariableByteDataModelElement('pid', dict),
				FixedDataModelElement('uid_str', b' uid='),
				VariableByteDataModelElement('uid', dict),
				FixedDataModelElement('old_auid_str', b' old-auid='),
				VariableByteDataModelElement('old_auid', dict),
                FixedDataModelElement('auid_str', b' auid='),
                VariableByteDataModelElement('auid', dict),
                OptionalMatchModelElement('tty', 
                	SequenceModelElement('tty', [
                		FixedDataModelElement('tty_str', b' tty='),
                		VariableByteDataModelElement('tty', dict)])),
				FixedDataModelElement('old_ses_str', b' old-ses='),
				VariableByteDataModelElement('old_ses', dict),
				FixedDataModelElement('ses_str', b' ses='),
				VariableByteDataModelElement('ses', dict),
				FixedDataModelElement('res_str', b' res='),
				VariableByteDataModelElement('res', dict)]),
			SequenceModelElement('sockaddr', [
				FixedDataModelElement('msg_str', b'SOCKADDR msg=audit('),
				DateTimeModelElement('time', b'%s.%f'),
				FixedDataModelElement('colon_str', b':'),
				DecimalIntegerValueModelElement('id'),
				FixedDataModelElement('saddr_str', b'): saddr='),
				VariableByteDataModelElement('saddr', dict)]),
			SequenceModelElement('unknown', [
				FixedDataModelElement('unknwon_str', b'UNKNOWN['),
				DecimalIntegerValueModelElement('unknown_id', value_sign_type = DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL),
				FixedDataModelElement('msg_str', b'] msg=audit('),
				DateTimeModelElement('time', b'%s.%f'),
				FixedDataModelElement('colon_str', b':'),
				DecimalIntegerValueModelElement('id'),
				FixedDataModelElement('proctitle_str', b'): proctitle='),
				VariableByteDataModelElement('proctitle', dict)]),
			SequenceModelElement('cred_refr', [
				FixedDataModelElement('msg1_str', b'CRED_REFR msg=')] + seq),
			SequenceModelElement('user_start', [
				FixedDataModelElement('msg1_str', b'USER_START msg=')] + seq),
			SequenceModelElement('user_acct', [
				FixedDataModelElement('msg1_str', b'USER_ACCT msg=')] + seq),
			SequenceModelElement('user_auth', [
				FixedDataModelElement('msg1_str', b'USER_AUTH msg=')] + seq),
			SequenceModelElement('cred_disp', [
				FixedDataModelElement('msg1_str', b'CRED_DISP msg=')] + seq),
			SequenceModelElement('service_start', [
				FixedDataModelElement('msg1_str', b'SERVICE_START msg=')] + seq),
			SequenceModelElement('service_stop', [
				FixedDataModelElement('msg1_str', b'SERVICE_STOP msg=')] + seq),
			SequenceModelElement('user_end', [
				FixedDataModelElement('msg1_str', b'USER_END msg=')] + seq),
			SequenceModelElement('user_cmd', [
                FixedDataModelElement('msg1_str', b'USER_CMD msg=')] + seq),
			SequenceModelElement('cred_acq', [
				FixedDataModelElement('msg1_str', b'CRED_ACQ msg=')] + seq),
			SequenceModelElement('user_bprm_fcaps', [
				FixedDataModelElement('msg1_str', b'BPRM_FCAPS msg=audit('),
				DateTimeModelElement('time', b'%s.%f'),
				FixedDataModelElement('colon_str', b':'),
				DecimalIntegerValueModelElement('id'),
				FixedDataModelElement('fver_str', b'): fver='),
				VariableByteDataModelElement('fver', dict),
				FixedDataModelElement('fp_str', b' fp='),
				VariableByteDataModelElement('fp', dict),
				FixedDataModelElement('fi_str', b' fi='),
				VariableByteDataModelElement('fi', dict),
				FixedDataModelElement('fe_str', b' fe='),
				VariableByteDataModelElement('fe', dict),
				FixedDataModelElement('old_pp_str', b' old_pp='),
				VariableByteDataModelElement('old_pp', dict),
				FixedDataModelElement('old_pi_str', b' old_pi='),
				VariableByteDataModelElement('old_pi', dict),
				FixedDataModelElement('old_pe_str', b' old_pe='),
				VariableByteDataModelElement('old_pe', dict),
				FixedDataModelElement('new_pp_str', b' new_pp='),
				VariableByteDataModelElement('new_pp', dict),
				FixedDataModelElement('new_pi_str', b' new_pi='),
				VariableByteDataModelElement('new_pi', dict),
				FixedDataModelElement('new_pe_str', b' new_pe='),
				VariableByteDataModelElement('new_pe', dict),])])])

	return model
