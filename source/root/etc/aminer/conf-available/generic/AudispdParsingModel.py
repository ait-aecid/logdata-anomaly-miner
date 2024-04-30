"""This module contains functions and classes to create the parsing model."""

from aminer.parsing.AnyByteDataModelElement import AnyByteDataModelElement
from aminer.parsing.DecimalIntegerValueModelElement import DecimalIntegerValueModelElement
from aminer.parsing.DecimalFloatValueModelElement import DecimalFloatValueModelElement
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
from aminer.parsing.ModelElementInterface import ModelElementInterface


def get_model():
    """Return a model to parse a audispd message logged via syslog after any
    standard logging preamble, e.g. from syslog."""

    class ExecArgumentDataModelElement(ModelElementInterface):
        """This is a helper class for parsing the (encoded) exec argument
        strings found within audit logs."""

        def get_match_element(self, target_path: str, match_context):
            """Find the maximum number of bytes belonging to an exec argument.

            @return a match when at least two bytes were found including the delimiters.
            """
            data = match_context.match_data
            match_len = 0
            if data[0] == ord(b'"'):
                match_len = data.find(b'"', 1)
                if match_len == -1:
                    return None
                match_value = data[1:match_len]
                match_len += 1
            elif data.startswith(b"(null)"):
                match_len = 6
                match_value = None
            else:
                # Must be upper case hex encoded:
                match_value = b""
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
            return MatchElement(f"{target_path}/{self.element_id}", match_data, match_value, None)

    pam_status_word_list = FixedWordlistDataModelElement("status", [b"failed", b"success"])

    pid = b" pid="
    uid = b" uid="
    auid = b" auid="
    gid = b" gid="
    ses = b" ses="
    exe = b' exe="'
    hostname = b'" hostname='
    hostname1 = b'" (hostname='
    addr = b" addr="
    addr1 = b", addr="
    terminal = b" terminal="
    terminal1 = b", terminal="
    res = b" res="
    exe1 = b'" exe="'
    subj = b" subj="
    comm = b" comm="
    reason = b" reason="
    dev = b" dev="
    sig = b" sig="
    alphabet = b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789._-"
    perms_alphabet = b"abcdefghijklmnopqrstuvwxyz,"

    type_branches = {
        "ADD_GROUP": SequenceModelElement("addgroup", [
            FixedDataModelElement("s0", pid),
            DecimalIntegerValueModelElement("pid"),
            FixedDataModelElement("s1", uid),
            DecimalIntegerValueModelElement("uid"),
            FixedDataModelElement("s2", auid),
            DecimalIntegerValueModelElement("auid"),
            FixedDataModelElement("s3", ses),
            DecimalIntegerValueModelElement("ses"),
            FixedDataModelElement("s4", subj),
            DelimitedDataModelElement("subj", b" "),
            FixedDataModelElement("s5", b" msg='op=adding group acct=\""),
            DelimitedDataModelElement("acct", b'"'),
            FixedDataModelElement("s6", b'"'),
            FixedDataModelElement("s7", exe),
            DelimitedDataModelElement("exec", b'"'),
            FixedDataModelElement("s8", hostname),
            DelimitedDataModelElement("clientname", b" "),
            FixedDataModelElement("s9", addr),
            DelimitedDataModelElement("clientip", b" "),
            FixedDataModelElement("s10", terminal),
            WhiteSpaceLimitedDataModelElement("terminal"),
            FixedDataModelElement("s11", res),
            pam_status_word_list,
            FixedDataModelElement("s12", b"'"),
        ]),
        "ADD_USER": SequenceModelElement("adduser", [
            FixedDataModelElement("s0", pid),
            DecimalIntegerValueModelElement("pid"),
            FixedDataModelElement("s1", uid),
            DecimalIntegerValueModelElement("uid"),
            FixedDataModelElement("s2", auid),
            DecimalIntegerValueModelElement("auid"),
            FixedDataModelElement("s3", ses),
            DecimalIntegerValueModelElement("ses"),
            FixedDataModelElement("s4", subj),
            DelimitedDataModelElement("subj", b" "),
            FixedWordlistDataModelElement("s5", [b" msg='op=adding user id=", b" msg='op=adding home directory id="]),
            DecimalIntegerValueModelElement("newuserid"),
            FixedDataModelElement("s6", exe),
            DelimitedDataModelElement("exec", b'"'),
            FixedDataModelElement("s7", hostname),
            DelimitedDataModelElement("clientname", b" "),
            FixedDataModelElement("s8", addr),
            DelimitedDataModelElement("clientip", b" "),
            FixedDataModelElement("s9", terminal),
            WhiteSpaceLimitedDataModelElement("terminal"),
            FixedDataModelElement("s10", res),
            pam_status_word_list,
            FixedDataModelElement("s11", b"'"),
        ]),
        "ANOM_ABEND": SequenceModelElement("anom_abend", [
            FixedDataModelElement("s0", auid),
            DecimalIntegerValueModelElement("auid"),
            FixedDataModelElement("s1", uid),
            DecimalIntegerValueModelElement("uid"),
            FixedDataModelElement("s2", gid),
            DecimalIntegerValueModelElement("gid"),
            FixedDataModelElement("s3", ses),
            DecimalIntegerValueModelElement("ses"),
            FixedDataModelElement("s4", subj),
            DelimitedDataModelElement("subj", b" "),
            FixedDataModelElement("s5", pid),
            DecimalIntegerValueModelElement("pid"),
            FixedDataModelElement("s6", comm),
            ExecArgumentDataModelElement("command"),
            FixedDataModelElement("s7", reason),
            ExecArgumentDataModelElement("reason"),
            FixedDataModelElement("s8", sig),
            DecimalIntegerValueModelElement("sig")
        ]),
        "ANOM_ACCESS_FS": AnyByteDataModelElement("anom_access_fs"),
        "ANOM_ADD_ACCT": AnyByteDataModelElement("anom_add_acct"),
        "ANOM_AMTU_FAIL": AnyByteDataModelElement("anom_amtu_fail"),
        "ANOM_CRYPTO_FAIL": AnyByteDataModelElement("anom_crypto_fail"),
        "ANOM_DEL_ACCT": AnyByteDataModelElement("anom_del_acct"),
        "ANOM_EXEC": SequenceModelElement("anom_exec", [
            FixedDataModelElement("space", b" "),
            VariableByteDataModelElement("user", alphabet),
            FixedDataModelElement("s0", pid),
            DecimalIntegerValueModelElement("pid"),
            FixedDataModelElement("s1", uid),
            DecimalIntegerValueModelElement("uid"),
            FixedDataModelElement("s2", auid),
            DecimalIntegerValueModelElement("auid"),
            FixedDataModelElement("s3", ses),
            DecimalIntegerValueModelElement("ses"),
            FixedDataModelElement("s4", b" msg='op="),
            DelimitedDataModelElement("msg", b" "),
            FixedDataModelElement("s5", b' acct="'),
            DelimitedDataModelElement("acct", b'"'),
            FixedDataModelElement("s6", exe1),
            DelimitedDataModelElement("exec", b'"'),
            FixedDataModelElement("s7", hostname1),
            DelimitedDataModelElement("hostname", b","),
            FixedDataModelElement("s8", addr1),
            DelimitedDataModelElement("addr", b","),
            FixedDataModelElement("s9", terminal1),
            DelimitedDataModelElement("terminal", b" "),
            FixedDataModelElement("s10", res),
            pam_status_word_list,
            FixedDataModelElement("s11", b")'")
        ]),
        "ANOM_LOGIN_ACCT": AnyByteDataModelElement("anom_login_acct"),
        "ANOM_LOGIN_FAILURES": AnyByteDataModelElement("anom_login_failures"),
        "ANOM_LOGIN_LOCATION": AnyByteDataModelElement("anom_login_location"),
        "ANOM_LOGIN_SESSIONS": AnyByteDataModelElement("anom_login_sessions"),
        "ANOM_LOGIN_TIME": AnyByteDataModelElement("anom_login_time"),
        "ANOM_MAX_DAC": AnyByteDataModelElement("anom_max_dac"),
        "ANOM_MAX_MAC": AnyByteDataModelElement("anom_max_mac"),
        "ANOM_MK_EXEC": AnyByteDataModelElement("anom_mk_exec"),
        "ANOM_MOD_ACCT": AnyByteDataModelElement("anom_mod_acct"),
        "ANOM_PROMISCUOUS": SequenceModelElement("anom_promiscuous", [
            FixedDataModelElement("s0", b" dev="),
            VariableByteDataModelElement("dev", alphabet),
            FixedDataModelElement("s1", b" prom="),
            DecimalIntegerValueModelElement("prom"),
            FixedDataModelElement("s2", b" old_prom="),
            DecimalIntegerValueModelElement("old_prom"),
            FixedDataModelElement("s3", auid),
            DecimalIntegerValueModelElement("auid"),
            FixedDataModelElement("s4", uid),
            DecimalIntegerValueModelElement("uid"),
            FixedDataModelElement("s5", gid),
            DecimalIntegerValueModelElement("gid"),
            FixedDataModelElement("s6", ses),
            DecimalIntegerValueModelElement("ses"),
        ]),
        "ANOM_RBAC_FAIL": AnyByteDataModelElement("anom_rbac_fail"),
        "ANOM_RBAC_INTEGRITY_FAIL": AnyByteDataModelElement("anom_rbac_integrity_fail"),
        "ANOM_ROOT_TRANS": AnyByteDataModelElement("anom_root_trans"),
        "AVC": AnyByteDataModelElement("avc"),
        "AVC_PATH": AnyByteDataModelElement("avc_path"),
        "BPRM_FCAPS": SequenceModelElement("bprmfcaps", [
            FixedDataModelElement("s0", b" fver="),
            DecimalIntegerValueModelElement("fver"),
            FixedDataModelElement("s1", b" fp="),
            HexStringModelElement("fp"),
            FixedDataModelElement("s2", b" fi="),
            HexStringModelElement("fi"),
            FixedDataModelElement("s3", b" fe="),
            HexStringModelElement("fe"),
            FixedDataModelElement("s4", b" old_pp="),
            DelimitedDataModelElement("pp-old", b" "),
            FixedDataModelElement("s5", b" old_pi="),
            DelimitedDataModelElement("pi-old", b' '),
            FixedDataModelElement("s6", b" old_pe="),
            DelimitedDataModelElement("pe-old", b" "),
            FixedDataModelElement("s7", b" new_pp="),
            DelimitedDataModelElement("pp-new", b" "),
            FixedDataModelElement("s8", b" new_pi="),
            DelimitedDataModelElement("pi-new", b" "),
            FixedDataModelElement("s9", b" new_pe="),
            AnyByteDataModelElement("pe-new")
        ]),
        "CAPSET": AnyByteDataModelElement("capset"),
        "CHGRP_ID": AnyByteDataModelElement("chgrp_id"),
        "CHUSER_ID": AnyByteDataModelElement("chuser_id"),
        "CONFIG_CHANGE": SequenceModelElement("conf-change", [
            FixedDataModelElement("s0", auid),
            DecimalIntegerValueModelElement("auid"),
            FixedDataModelElement("s1", ses),
            DecimalIntegerValueModelElement("ses"),
            FixedDataModelElement("s2", b' op="'),
            DelimitedDataModelElement("op", b'"'),
            FixedDataModelElement("s3", b'" path="'),
            DelimitedDataModelElement("path", b'"'),
            FixedDataModelElement("s4", b'" key='),
            DelimitedDataModelElement("key", b" "),
            FixedDataModelElement("s5", b' list='),
            DecimalIntegerValueModelElement("list"),
            FixedDataModelElement("s6", res),
            DecimalIntegerValueModelElement("result")
        ]),
        "CRED_ACQ": SequenceModelElement("credacq", [
            FixedDataModelElement("s0", pid),
            DecimalIntegerValueModelElement("pid"),
            FixedDataModelElement("s1", uid),
            DecimalIntegerValueModelElement("uid"),
            FixedDataModelElement("s2", auid),
            DecimalIntegerValueModelElement("auid"),
            FixedDataModelElement("s3", ses),
            DecimalIntegerValueModelElement("ses"),
            FixedDataModelElement("s4", b' msg=\'op=PAM:setcred acct="'),
            DelimitedDataModelElement("username", b'"'),
            FixedDataModelElement("s5", exe1),
            DelimitedDataModelElement("exec", b'"'),
            FixedDataModelElement("s6", hostname),
            DelimitedDataModelElement("clientname", b" "),
            FixedDataModelElement("s7", addr),
            DelimitedDataModelElement("clientip", b" "),
            FixedDataModelElement("s8", terminal),
            WhiteSpaceLimitedDataModelElement("terminal"),
            FixedDataModelElement("s9", res),
            pam_status_word_list,
            FixedDataModelElement("s10", b"'"),
        ]),
        "CRED_DISP": SequenceModelElement("creddisp", [
            FixedDataModelElement("s0", pid),
            DecimalIntegerValueModelElement("pid"),
            FixedDataModelElement("s1", uid),
            DecimalIntegerValueModelElement("uid"),
            FixedDataModelElement("s2", auid),
            DecimalIntegerValueModelElement("auid"),
            FixedDataModelElement("s3", ses),
            DecimalIntegerValueModelElement("ses"),
            FixedDataModelElement("s4", b' msg=\'op=PAM:setcred acct="'),
            DelimitedDataModelElement("username", b'"'),
            FixedDataModelElement("s5", exe1),
            DelimitedDataModelElement("exec", b'"'),
            FixedDataModelElement("s6", hostname),
            DelimitedDataModelElement("clientname", b" "),
            FixedDataModelElement("s7", addr),
            DelimitedDataModelElement("clientip", b" "),
            FixedDataModelElement("s8", terminal),
            WhiteSpaceLimitedDataModelElement("terminal"),
            FixedDataModelElement("s9", res),
            pam_status_word_list,
            FixedDataModelElement("s10", b"'"),
        ]),
        "CRED_REFR": SequenceModelElement("creddisp", [
            FixedDataModelElement("s0", pid),
            DecimalIntegerValueModelElement("pid"),
            FixedDataModelElement("s1", uid),
            DecimalIntegerValueModelElement("uid"),
            FixedDataModelElement("s2", auid),
            DecimalIntegerValueModelElement("auid"),
            FixedDataModelElement("s3", ses),
            DecimalIntegerValueModelElement("ses"),
            FixedDataModelElement("s4", b' msg=\'op=PAM:setcred acct="root" exe="/usr/sbin/sshd" hostname='),
            IpAddressDataModelElement("clientname"),
            FixedDataModelElement("s5", addr),
            IpAddressDataModelElement("clientip"),
            FixedDataModelElement("s6", terminal),
            DelimitedDataModelElement("terminal", b" "),
            FixedDataModelElement("s7", res),
            pam_status_word_list,
            FixedDataModelElement("s8", b"'"),
        ]),
        "CRYPTO_FAILURE_USER": AnyByteDataModelElement("crypto_failure_user"),
        "CRYPTO_KEY_USER": AnyByteDataModelElement("crypto_key_user"),
        "CRYPTO_LOGIN": AnyByteDataModelElement("crypto_login"),
        "CRYPTO_LOGOUT": AnyByteDataModelElement("crypto_logout"),
        "CRYPTO_PARAM_CHANGE_USER": AnyByteDataModelElement("crypto_param_change_user"),
        "CRYPTO_REPLAY_USER": AnyByteDataModelElement("crypto_replay_user"),
        "CRYPTO_SESSION": SequenceModelElement("crypto_session", [
            FixedDataModelElement("space", b" "),
            VariableByteDataModelElement("user", alphabet),
            FixedDataModelElement("s0", pid),
            DecimalIntegerValueModelElement("pid"),
            FixedDataModelElement("s1", uid),
            DecimalIntegerValueModelElement("uid"),
            FixedDataModelElement("s2", auid),
            DecimalIntegerValueModelElement("auid"),
            FixedDataModelElement("s4", b" msg='op="),
            DelimitedDataModelElement("msg", b" "),
            FixedDataModelElement("s5", b' direction='),
            DelimitedDataModelElement("direction", b' '),
            FixedDataModelElement("s6", b' cipher='),
            DelimitedDataModelElement("cipher", b' '),
            FixedDataModelElement("s7", b' ksize='),
            DecimalIntegerValueModelElement("ksize"),
            FixedDataModelElement("s8", b' rport='),
            DecimalIntegerValueModelElement("rport"),
            FixedDataModelElement("s9", b' laddr='),
            IpAddressDataModelElement("laddr"),
            FixedDataModelElement("s10", b' lport='),
            DecimalIntegerValueModelElement("lport"),
            FixedDataModelElement("s11", b' id='),
            DecimalIntegerValueModelElement("id"),
            FixedDataModelElement("s12", exe),
            DelimitedDataModelElement("exec", b'"'),
            FixedDataModelElement("s13", hostname1),
            DelimitedDataModelElement("hostname", b","),
            FixedDataModelElement("s14", addr1),
            DelimitedDataModelElement("addr", b","),
            FixedDataModelElement("s15", terminal1),
            DelimitedDataModelElement("terminal", b" "),
            FixedDataModelElement("s16", res),
            pam_status_word_list,
            FixedDataModelElement("s17", b")'")
        ]),
        "CRYPTO_TEST_USER": AnyByteDataModelElement("crypto_test_user"),
        "CWD": SequenceModelElement("cwd", [
            FixedDataModelElement("s0", b"  cwd="),
            ExecArgumentDataModelElement("cwd")]),
        "DAC_CHECK": AnyByteDataModelElement("dac_check"),
        "DAEMON_ABORT": SequenceModelElement("daemon_abort", [
            FixedDataModelElement("s0", b" auditd error halt,"),
            FixedDataModelElement("s1", auid),
            DecimalIntegerValueModelElement("auid"),
            FixedDataModelElement("s2", pid),
            DecimalIntegerValueModelElement("pid"),
            FixedDataModelElement("s3", res),
            pam_status_word_list
        ]),
        "DAEMON_ACCEPT": AnyByteDataModelElement("daemon_accept"),
        "DAEMON_CLOSE": AnyByteDataModelElement("daemon_close"),
        "DAEMON_CONFIG": SequenceModelElement("daemon_config", [
            FixedDataModelElement("s0", b" auditd error getting hup info - no change, sending"),
            FixedDataModelElement("s1", auid),
            DelimitedDataModelElement("auid", b" "),
            FixedDataModelElement("s2", pid),
            DelimitedDataModelElement("pid", b" "),
            FixedDataModelElement("s3", subj),
            DelimitedDataModelElement("subj", b" "),
            FixedDataModelElement("s4", res),
            pam_status_word_list
        ]),
        "DAEMON_END": SequenceModelElement("daemon_end", [
            FixedDataModelElement("s0", b" auditd normal halt, sending"),
            FixedDataModelElement("s1", auid),
            DelimitedDataModelElement("auid", b" "),
            FixedDataModelElement("s2", pid),
            DelimitedDataModelElement("pid", b" "),
            FixedDataModelElement("s3", subj),
            OptionalMatchModelElement("optional_subj", DelimitedDataModelElement("subj", b" ")),
            FixedDataModelElement("s4", res),
            pam_status_word_list
        ]),
        "DAEMON_RESUME": SequenceModelElement("daemon_resume", [
            FixedDataModelElement("s0", b" auditd resuming logging, sending"),
            FixedDataModelElement("s1", auid),
            DelimitedDataModelElement("auid", b" "),
            FixedDataModelElement("s2", pid),
            DelimitedDataModelElement("pid", b" "),
            FixedDataModelElement("s3", subj),
            DelimitedDataModelElement("subj", b" "),
            FixedDataModelElement("s4", res),
            pam_status_word_list
        ]),
        "DAEMON_ROTATE": AnyByteDataModelElement("daemon_rotate"),
        "DAEMON_START": SequenceModelElement("daemon_start", [
            FixedDataModelElement("s0", b" auditd start, ver="),
            DecimalFloatValueModelElement("ver"),
            FixedDataModelElement("s1", b" format="),
            DelimitedDataModelElement("format", b" "),
            FixedDataModelElement("s2", b" kernel="),
            DelimitedDataModelElement("kernel", b" "),
            FixedDataModelElement("s3", auid),
            DelimitedDataModelElement("auid", b" "),
            FixedDataModelElement("s4", pid),
            DelimitedDataModelElement("pid", b" "),
            FixedDataModelElement("s5", res),
            pam_status_word_list
        ]),
        "DEL_GROUP": AnyByteDataModelElement("del_group"),
        "DEL_USER": AnyByteDataModelElement("del_user"),
        "EOE": AnyByteDataModelElement("eoe"),
        "EXECVE": SequenceModelElement("execve", [
            FixedDataModelElement("s0", b" argc="),
            DecimalIntegerValueModelElement("argc"),
            # We need a type branch here also, but there is no additional data in EOE records after Ubuntu Trusty any more.
            RepeatedElementDataModelElement("arg", SequenceModelElement("execarg", [
                FixedDataModelElement("s0", b" a"),
                DecimalIntegerValueModelElement("argn"),
                FixedDataModelElement("s1", b"="),
                ExecArgumentDataModelElement("argval")
            ]))
        ]),
        "FD_PAIR": SequenceModelElement("fdpair", [
            FixedDataModelElement("s0", b" fd0="),
            DecimalIntegerValueModelElement("fd0"),
            FixedDataModelElement("s1", b" fd1="),
            DecimalIntegerValueModelElement("fd1")
        ]),
        "FS_RELABEL": AnyByteDataModelElement("fs_relabel"),
        "GRP_AUTH": AnyByteDataModelElement("grp_auth"),
        "INTEGRITY_DATA": AnyByteDataModelElement("integrity_data"),
        "INTEGRITY_HASH": AnyByteDataModelElement("integrity_hash"),
        "INTEGRITY_METADATA": AnyByteDataModelElement("integrity_metadata"),
        "INTEGRITY_PCR": AnyByteDataModelElement("integrity_pcr"),
        "INTEGRITY_RULE": AnyByteDataModelElement("integrity_rule"),
        "INTEGRITY_STATUS": AnyByteDataModelElement("integrity_status"),
        "IPC": AnyByteDataModelElement("ipc"),
        "IPC_SET_PERM": AnyByteDataModelElement("ipc_set_perm"),
        "KERNEL": AnyByteDataModelElement("kernel"),
        "KERNEL_OTHER": AnyByteDataModelElement("kernel_other"),
        "LABEL_LEVEL_CHANGE": AnyByteDataModelElement("label_level_change"),
        "LABEL_OVERRIDE": AnyByteDataModelElement("label_override"),
        # This message differs on Ubuntu 32/64 bit variants.
        "LOGIN": SequenceModelElement("login", [
            FixedDataModelElement("s0", b" login"),
            FixedDataModelElement("s1", pid),
            DecimalIntegerValueModelElement("pid"),
            FixedDataModelElement("s2", uid),
            DecimalIntegerValueModelElement("uid"),
            FixedWordlistDataModelElement("s3", [b" old auid=", b" old-auid="]),
            DecimalIntegerValueModelElement("auid-old"),
            FixedWordlistDataModelElement("s4", [b" new auid=", auid]),
            DecimalIntegerValueModelElement("auid-new"),
            FixedWordlistDataModelElement("s5", [b" old ses=", b" old-ses="]),
            DecimalIntegerValueModelElement("ses-old"),
            FixedWordlistDataModelElement("s6", [b" new ses=", ses]),
            DecimalIntegerValueModelElement("ses-new"),
            OptionalMatchModelElement("optional_result", SequenceModelElement("result_seq", [
                FixedDataModelElement("s7", res),
                DecimalIntegerValueModelElement("result")
            ]))
        ]),
        "MAC_CIPSOV4_ADD": AnyByteDataModelElement("mac_cipsov4_add"),
        "MAC_CIPSOV4_DEL": AnyByteDataModelElement("mac_cipsov4_del"),
        "MAC_CONFIG_CHANGE": AnyByteDataModelElement("mac_config_change"),
        "MAC_IPSEC_EVENT": AnyByteDataModelElement("mac_ipsec_event"),
        "MAC_MAP_ADD": AnyByteDataModelElement("mac_map_add"),
        "MAC_MAP_DEL": AnyByteDataModelElement("mac_map_del"),
        "MAC_POLICY_LOAD": AnyByteDataModelElement("mac_policy_load"),
        "MAC_STATUS": SequenceModelElement("mac_status", [
            FixedDataModelElement("s0", b" enforcing="),
            DecimalIntegerValueModelElement("enforcing"),
            FixedDataModelElement("s1", b" old_enforcing="),
            DecimalIntegerValueModelElement("old_enforcing"),
            FixedDataModelElement("s2", auid),
            DelimitedDataModelElement("auid", b" "),
            FixedDataModelElement("s3", ses),
            DecimalIntegerValueModelElement("ses")
        ]),
        "MAC_UNLBL_ALLOW": AnyByteDataModelElement("mac_unlbl_allow"),
        "MAC_UNLBL_STCADD": AnyByteDataModelElement("mac_unlbl_stcadd"),
        "MAC_UNLBL_STCDEL": AnyByteDataModelElement("mac_unlbl_stcdel"),
        "MMAP": AnyByteDataModelElement("mmap"),
        "MQ_GETSETATTR": AnyByteDataModelElement("mq_getsetattr"),
        "MQ_NOTIFY": AnyByteDataModelElement("mq_notify"),
        "MQ_OPEN": AnyByteDataModelElement("mq_open"),
        "MQ_SENDRECV": AnyByteDataModelElement("mq_sendrecv"),
        "NETFILTER_CFG": SequenceModelElement("netfilter_cfg", [
            FixedDataModelElement("s0", b" table="),
            FixedWordlistDataModelElement("table", [b"filter", b"mangle", b"nat"]),
            FixedDataModelElement("s1", b" family="),
            DecimalIntegerValueModelElement("family"),
            FixedDataModelElement("s2", b" entries="),
            DecimalIntegerValueModelElement("entries")
        ]),
        "NETFILTER_PKT": SequenceModelElement("netfilter_pkt", [
            FixedDataModelElement("s0", b" mark=0x"),
            HexStringModelElement("mark"),
            FixedDataModelElement("s1", b" saddr="),
            FirstMatchModelElement("saddr", [
                IpAddressDataModelElement("ipv4"),
                IpAddressDataModelElement("ipv6", ipv6=True),
            ]),
            FixedDataModelElement("s2", b" daddr="),
            FirstMatchModelElement("daddr", [
                IpAddressDataModelElement("ipv4"),
                IpAddressDataModelElement("ipv6", ipv6=True),
            ]),
            FixedDataModelElement("s3", b" proto="),
            DecimalIntegerValueModelElement("proto")
        ]),
        "OBJ_PID": SequenceModelElement("objpid", [
            FixedDataModelElement("s0", b" opid="),
            DecimalIntegerValueModelElement("opid"),
            FixedDataModelElement("s1", b" oauid="),
            DecimalIntegerValueModelElement("oauid", value_sign_type=DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL),
            FixedDataModelElement("s2", b" ouid="),
            DecimalIntegerValueModelElement("ouid"),
            FixedDataModelElement("s3", b" oses="),
            DecimalIntegerValueModelElement("oses", value_sign_type=DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL),
            FixedDataModelElement("s4", b" obj="),
            DelimitedDataModelElement("obj", b" "),
            FixedDataModelElement("s4", b" ocomm="),
            ExecArgumentDataModelElement("ocomm")
        ]),
        "PATH": SequenceModelElement("path", [
            FixedDataModelElement("s0", b" item="),
            DecimalIntegerValueModelElement("item"),
            FixedDataModelElement("s1", b" name="),
            ExecArgumentDataModelElement("name"),
            FirstMatchModelElement("fsinfo", [
                SequenceModelElement("inodeinfo", [
                    FixedDataModelElement("s0", b" inode="),
                    DecimalIntegerValueModelElement("inode"),
                    FixedDataModelElement("s1", dev),
                    # A special major/minor device element could be better here.
                    VariableByteDataModelElement("dev", b"0123456789abcdef:"),
                    FixedDataModelElement("s2", b" mode="),
                    # is octal
                    DecimalIntegerValueModelElement("mode", value_pad_type=DecimalIntegerValueModelElement.PAD_TYPE_ZERO),
                    FixedDataModelElement("s3", b" ouid="),
                    DecimalIntegerValueModelElement("ouid"),
                    FixedDataModelElement("s4", b" ogid="),
                    DecimalIntegerValueModelElement("ogid"),
                    FixedDataModelElement("s5", b" rdev="),
                    # A special major/minor device element could be better here (see above).
                    VariableByteDataModelElement("rdev", b"0123456789abcdef:"),
                    FixedDataModelElement("s6", b" nametype=")
                ]),
                FixedDataModelElement("noinfo", b" nametype=")]),
            FixedWordlistDataModelElement("nametype", [b"CREATE", b"DELETE", b"NORMAL", b"PARENT", b"UNKNOWN"])
        ]),
        "PROCTITLE": SequenceModelElement("proctitle", [
            FixedDataModelElement("s0", b" proctitle="),
            ExecArgumentDataModelElement("proctitle")]),
        "RESP_ACCT_LOCK": AnyByteDataModelElement("resp_acct_lock"),
        "RESP_ACCT_LOCK_TIMED": AnyByteDataModelElement("resp_acct_lock_timed"),
        "RESP_ACCT_REMOTE": AnyByteDataModelElement("resp_acct_remote"),
        "RESP_ACCT_UNLOCK_TIMED": AnyByteDataModelElement("resp_acct_unlock_timed"),
        "RESP_ALERT": AnyByteDataModelElement("resp_alert"),
        "RESP_ANOMALY": AnyByteDataModelElement("resp_anomaly"),
        "RESP_EXEC": AnyByteDataModelElement("resp_exec"),
        "RESP_HALT": AnyByteDataModelElement("resp_halt"),
        "RESP_KILL_PROC": AnyByteDataModelElement("resp_kill_proc"),
        "RESP_SEBOOL": AnyByteDataModelElement("resp_sebool"),
        "RESP_SINGLE": AnyByteDataModelElement("resp_single"),
        "RESP_TERM_ACCESS": AnyByteDataModelElement("resp_term_access"),
        "RESP_TERM_LOCK": AnyByteDataModelElement("resp_term_lock"),
        "ROLE_ASSIGN": AnyByteDataModelElement("role_assign"),
        "ROLE_MODIFY": AnyByteDataModelElement("role_modify"),
        "ROLE_REMOVE": AnyByteDataModelElement("role_remove"),
        "SELINUX_ERR": SequenceModelElement("service_err", [
            FixedDataModelElement("s0", b" op="),
            DelimitedDataModelElement("op", b" "),
            FixedDataModelElement("s1", reason),
            DelimitedDataModelElement("reason", b" "),
            FixedDataModelElement("s2", b" scontext="),
            DelimitedDataModelElement("scontext", b" "),
            FixedDataModelElement("s3", b" tcontext="),
            DelimitedDataModelElement("tcontext", b" "),
            FixedDataModelElement("s4", b" tclass="),
            DelimitedDataModelElement("tclass", b" "),
            FixedDataModelElement("s5", b" perms="),
            VariableByteDataModelElement("perms", perms_alphabet)
        ]),
        "SERVICE_START": SequenceModelElement("service", [
            FixedDataModelElement("s0", pid),
            DecimalIntegerValueModelElement("pid"),
            FixedDataModelElement("s1", uid),
            DecimalIntegerValueModelElement("uid"),
            FixedDataModelElement("s2", auid),
            DecimalIntegerValueModelElement("auid"),
            FixedDataModelElement("s3", ses),
            DecimalIntegerValueModelElement("ses"),
            FixedDataModelElement("s4", b" msg='"),
            OptionalMatchModelElement("optional_msg", DelimitedDataModelElement("msg", b" ")),
            FixedDataModelElement("s5", b' comm="'),
            DelimitedDataModelElement("comm", b'"'),
            FixedDataModelElement("s5", b'" exe="'),
            DelimitedDataModelElement("exec", b'"'),
            FixedDataModelElement("s6", hostname),
            DelimitedDataModelElement("clientname", b" "),
            FixedDataModelElement("s7", addr),
            DelimitedDataModelElement("clientip", b" "),
            FixedDataModelElement("s8", terminal),
            WhiteSpaceLimitedDataModelElement("terminal"),
            FixedDataModelElement("s9", res),
            pam_status_word_list,
            FixedDataModelElement("s10", b"'")
        ]),
        "SOCKADDR": SequenceModelElement("sockaddr", [
            FixedDataModelElement("s0", b" saddr="),
            HexStringModelElement("sockaddr", upper_case=True)
        ]),
        "SOCKETCALL": SequenceModelElement("socketcall", [
            FixedDataModelElement("s0", b" nargs="),
            DecimalIntegerValueModelElement("nargs"),
            RepeatedElementDataModelElement("args", SequenceModelElement("arg", [
                FixedDataModelElement("s1", b" a"),
                DecimalIntegerValueModelElement("arg_num"),
                FixedDataModelElement("s2", b"="),
                DecimalIntegerValueModelElement("arg"),
            ]))
        ]),
        "SYSCALL": SequenceModelElement("syscall", [
            FixedDataModelElement("s0", b" arch="),
            HexStringModelElement("arch"),
            FixedDataModelElement("s1", b" syscall="),
            DecimalIntegerValueModelElement("syscall"),
            OptionalMatchModelElement(
                "personality", SequenceModelElement("pseq", [
                    FixedDataModelElement("s0", b" per="),
                    DecimalIntegerValueModelElement("personality")
                ])),
            OptionalMatchModelElement("result", SequenceModelElement("rseq", [
                FixedDataModelElement("s2", b" success="),
                FixedWordlistDataModelElement("succes", [b"no", b"yes"]),
                FixedDataModelElement("s3", b" exit="),
                DecimalIntegerValueModelElement("exit", value_sign_type=DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL)
            ])),
            FixedDataModelElement("s4", b" a0="),
            HexStringModelElement("arg0"),
            FixedDataModelElement("s5", b" a1="),
            HexStringModelElement("arg1"),
            FixedDataModelElement("s6", b" a2="),
            HexStringModelElement("arg2"),
            FixedDataModelElement("s7", b" a3="),
            HexStringModelElement("arg3"),
            FixedDataModelElement("s8", b" items="),
            DecimalIntegerValueModelElement("items"),
            FixedDataModelElement("s9", b" ppid="),
            DecimalIntegerValueModelElement("ppid"),
            FixedDataModelElement("s10", pid),
            DecimalIntegerValueModelElement("pid"),
            FixedDataModelElement("s11", auid),
            DecimalIntegerValueModelElement("auid"),
            FixedDataModelElement("s12", uid),
            DecimalIntegerValueModelElement("uid"),
            FixedDataModelElement("s13", gid),
            DecimalIntegerValueModelElement("gid"),
            FixedDataModelElement("s14", b" euid="),
            DecimalIntegerValueModelElement("euid"),
            FixedDataModelElement("s15", b" suid="),
            DecimalIntegerValueModelElement("suid"),
            FixedDataModelElement("s16", b" fsuid="),
            DecimalIntegerValueModelElement("fsuid"),
            FixedDataModelElement("s17", b" egid="),
            DecimalIntegerValueModelElement("egid"),
            FixedDataModelElement("s18", b" sgid="),
            DecimalIntegerValueModelElement("sgid"),
            FixedDataModelElement("s19", b" fsgid="),
            DecimalIntegerValueModelElement("fsgid"),
            FixedDataModelElement("s20", b" tty="),
            DelimitedDataModelElement("tty", b" "),
            FixedDataModelElement("s21", ses),
            DecimalIntegerValueModelElement("sesid"),
            FixedDataModelElement("s22", comm),
            ExecArgumentDataModelElement("command"),
            FixedDataModelElement("s23", exe),
            DelimitedDataModelElement("executable", b'"'),
            FixedDataModelElement("s24", b'" key='),
            AnyByteDataModelElement("key")
        ]),
        "SYSTEM_BOOT": AnyByteDataModelElement("system_boot"),
        "SYSTEM_RUNLEVEL": AnyByteDataModelElement("system_runlevel"),
        "SYSTEM_SHUTDOWN": AnyByteDataModelElement("system_shutdown"),
        "TRUSTED_APP": AnyByteDataModelElement("trusted_app"),
        "TTY": AnyByteDataModelElement("tty"),
        # The UNKNOWN type is used then audispd does not know the type of the event, usually because the kernel is more recent than audispd,
        # thus emiting yet unknown event types.
        # * type=1327: procitle: see https://www.redhat.com/archives/linux-audit/2014-February/msg00047.html
        "UNKNOWN[1327]": SequenceModelElement("unknown-proctitle", [
            FixedDataModelElement("s0", b" proctitle="),
            ExecArgumentDataModelElement("proctitle")
        ]),
        "USER_ACCT": SequenceModelElement("useracct", [
            FixedDataModelElement("space", b" "),
            DelimitedDataModelElement("user", b" "),
            FixedDataModelElement("s0", pid),
            DecimalIntegerValueModelElement("pid"),
            FixedDataModelElement("s1", uid),
            DecimalIntegerValueModelElement("uid"),
            FixedDataModelElement("s2", auid),
            DecimalIntegerValueModelElement("auid"),
            FixedDataModelElement("s3", ses),
            DecimalIntegerValueModelElement("ses"),
            FixedDataModelElement("s4", b' msg=\'op=PAM:accounting acct="'),
            DelimitedDataModelElement("username", b'"'),
            FixedDataModelElement("s5", exe1),
            DelimitedDataModelElement("exec", b'"'),
            FixedDataModelElement("s6", hostname1),
            DelimitedDataModelElement("clientname", b" "),
            FixedDataModelElement("s7", addr),
            DelimitedDataModelElement("clientip", b" "),
            FixedDataModelElement("s8", terminal),
            WhiteSpaceLimitedDataModelElement("terminal"),
            FixedDataModelElement("s9", res),
            pam_status_word_list,
            FixedDataModelElement("s10", b")'")
        ]),
        "USER_AUTH": SequenceModelElement("userauth", [
            FixedDataModelElement("s0", pid),
            DecimalIntegerValueModelElement("pid"),
            FixedDataModelElement("s1", uid),
            DecimalIntegerValueModelElement("uid"),
            FixedDataModelElement("s2", auid),
            DecimalIntegerValueModelElement("auid"),
            FixedDataModelElement("s3", ses),
            DecimalIntegerValueModelElement("ses"),
            FixedDataModelElement("s4", b' msg=\'op=PAM:authentication acct="'),
            DelimitedDataModelElement("username", b'"'),
            FixedDataModelElement("s5", exe1),
            DelimitedDataModelElement("exec", b'"'),
            FixedDataModelElement("s6", hostname),
            DelimitedDataModelElement("clientname", b" "),
            FixedDataModelElement("s7", addr),
            DelimitedDataModelElement("clientip", b" "),
            FixedDataModelElement("s8", terminal),
            WhiteSpaceLimitedDataModelElement("terminal"),
            FixedDataModelElement("s9", res),
            pam_status_word_list,
            FixedDataModelElement("s10", b"'")
        ]),
        "USER_AVC": AnyByteDataModelElement("user_avc"),
        "USER_CHAUTHTOK": AnyByteDataModelElement("user_chauthtok"),
        "USER_CMD": SequenceModelElement("user_cmd", [
            FixedDataModelElement("space", b" "),
            DelimitedDataModelElement("user", b" "),
            FixedDataModelElement("s0", pid),
            DecimalIntegerValueModelElement("pid"),
            FixedDataModelElement("s1", uid),
            DecimalIntegerValueModelElement("uid"),
            FixedDataModelElement("s2", auid),
            DecimalIntegerValueModelElement("auid"),
            FixedDataModelElement("s3", b" msg='"),
            DelimitedDataModelElement("msg", b" "),
            FixedDataModelElement("s4", b' cmd="'),
            DelimitedDataModelElement("cmd", b'"'),
            FixedDataModelElement("s5", b"\" (terminal=pts/0"),
            FixedDataModelElement("s6", res),
            pam_status_word_list,
            FixedDataModelElement("s7", b")'"),
        ]),
        "USER_END": SequenceModelElement("userend", [
            FixedDataModelElement("space", b" "),
            DelimitedDataModelElement("user", b" "),
            FixedDataModelElement("s0", pid),
            DecimalIntegerValueModelElement("pid"),
            FixedDataModelElement("s1", uid),
            DecimalIntegerValueModelElement("uid"),
            FixedDataModelElement("s2", auid),
            DecimalIntegerValueModelElement("auid"),
            FixedDataModelElement("s4", b' msg=\'PAM: session close acct="'),
            DelimitedDataModelElement("username", b'"'),
            FixedDataModelElement("s5", b'" :' + exe),
            DelimitedDataModelElement("exec", b'"'),
            FixedDataModelElement("s6", hostname1),
            DelimitedDataModelElement("clientname", b" "),
            FixedDataModelElement("s7", addr),
            DelimitedDataModelElement("clientip", b" "),
            FixedDataModelElement("s8", terminal),
            WhiteSpaceLimitedDataModelElement("terminal"),
            FixedDataModelElement("s9", res),
            pam_status_word_list,
            FixedDataModelElement("s10", b")'"),
        ]),
        "USER_ERR": SequenceModelElement("usererr", [
            FixedDataModelElement("space", b" "),
            DelimitedDataModelElement("user", b" "),
            FixedDataModelElement("s0", pid),
            DecimalIntegerValueModelElement("pid"),
            FixedDataModelElement("s1", uid),
            DecimalIntegerValueModelElement("uid"),
            FixedDataModelElement("s2", auid),
            DecimalIntegerValueModelElement("auid"),
            FixedDataModelElement("s3", b' msg=\'PAM: bad_ident acct=? : exe="'),
            DelimitedDataModelElement("exec", b'"'),
            FixedDataModelElement("s4", hostname1),
            DelimitedDataModelElement("clientname", b" "),
            FixedDataModelElement("s5", addr),
            DelimitedDataModelElement("clientip", b" "),
            FixedDataModelElement("s6", terminal),
            WhiteSpaceLimitedDataModelElement("terminal"),
            FixedDataModelElement("s7", res),
            pam_status_word_list,
            FixedDataModelElement("s8", b")'")
        ]),
        "USER_LABELED_EXPORT": AnyByteDataModelElement("user_labeled_export"),
        "USER_LOGIN": SequenceModelElement("userlogin", [
            FixedDataModelElement("space", b" "),
            DelimitedDataModelElement("user", b" "),
            FixedDataModelElement("s0", pid),
            DecimalIntegerValueModelElement("pid"),
            FixedDataModelElement("s1", uid),
            DecimalIntegerValueModelElement("uid"),
            FixedDataModelElement("s2", auid),
            DecimalIntegerValueModelElement("auid"),
            FixedDataModelElement("s3", b" msg='acct=\""),
            DelimitedDataModelElement("acct", b'"'),
            FixedDataModelElement("s4", b'":' + exe),
            DelimitedDataModelElement("exec", b'"'),
            FixedDataModelElement("s5", hostname1),
            DelimitedDataModelElement("clientname", b" "),
            FixedDataModelElement("s6", addr),
            DelimitedDataModelElement("clientip", b" "),
            FixedDataModelElement("s7", terminal),
            WhiteSpaceLimitedDataModelElement("terminal"),
            FixedDataModelElement("s8", res),
            pam_status_word_list,
            FixedDataModelElement("s9", b")'")
        ]),
        "USER_LOGOUT": AnyByteDataModelElement("user_logout"),
        "USER_MAC_POLICY_LOAD": AnyByteDataModelElement("user_mac_policy_load"),
        "USER_MGMT": AnyByteDataModelElement("user_mgmt"),
        "USER_ROLE_CHANGE": SequenceModelElement("user_role_change", [
            FixedDataModelElement("space", b" "),
            DelimitedDataModelElement("user", b" "),
            FixedDataModelElement("s0", pid),
            DecimalIntegerValueModelElement("pid"),
            FixedDataModelElement("s1", uid),
            DecimalIntegerValueModelElement("uid"),
            FixedDataModelElement("s2", auid),
            DecimalIntegerValueModelElement("auid"),
            FixedDataModelElement("s3", subj),
            DelimitedDataModelElement("subj", b" "),
            FixedDataModelElement("s4", b" msg='pam: "),
            DelimitedDataModelElement("msg", b" "),
            FixedDataModelElement("s5", b" selected-context="),
            DelimitedDataModelElement("selected_context", b" "),
            FixedDataModelElement("s6", exe),
            DelimitedDataModelElement("exec", b'"'),
            FixedDataModelElement("s7", hostname1),
            DelimitedDataModelElement("clientname", b" "),
            FixedDataModelElement("s8", addr),
            DelimitedDataModelElement("clientip", b" "),
            FixedDataModelElement("s9", terminal),
            WhiteSpaceLimitedDataModelElement("terminal"),
            FixedDataModelElement("s10", res),
            pam_status_word_list,
            FixedDataModelElement("s11", b")'")
        ]),
        "USER_SELINUX_ERR": AnyByteDataModelElement("user_selinux_err"),
        "USER_START": SequenceModelElement("userstart", [
            FixedDataModelElement("space", b" "),
            DelimitedDataModelElement("user", b" "),
            FixedDataModelElement("s0", pid),
            DecimalIntegerValueModelElement("pid"),
            FixedDataModelElement("s1", uid),
            DecimalIntegerValueModelElement("uid"),
            FixedDataModelElement("s2", auid),
            DecimalIntegerValueModelElement("auid"),
            FixedDataModelElement("s3", b' msg=\'PAM: session open acct="'),
            DelimitedDataModelElement("username", b'"'),
            FixedDataModelElement("s4", b'" :' + exe),
            DelimitedDataModelElement("exec", b'"'),
            FixedDataModelElement("s5", hostname1),
            DelimitedDataModelElement("clientname", b" "),
            FixedDataModelElement("s6", addr),
            DelimitedDataModelElement("clientip", b" "),
            FixedDataModelElement("s7", terminal),
            WhiteSpaceLimitedDataModelElement("terminal"),
            FixedDataModelElement("s8", res),
            pam_status_word_list,
            FixedDataModelElement("s9", b")'"),
        ]),
        "USER_TTY": AnyByteDataModelElement("user_tty"),
        "USER_UNLABELED_EXPORT": AnyByteDataModelElement("user_unlabeled_export"),
        "USYS_CONFIG": AnyByteDataModelElement("usys_config"),
        "VIRT_CONTROL": AnyByteDataModelElement("virt_control"),
        "VIRT_MACHINE_ID": AnyByteDataModelElement("virt_machine_id"),
        "VIRT_RESOURCE": AnyByteDataModelElement("virt_resource")
    }

    type_branches["SERVICE_STOP"] = type_branches["SERVICE_START"]

    model = SequenceModelElement("audispd", [
        OptionalMatchModelElement("optional", FirstMatchModelElement("type", [
            FixedDataModelElement("sname", b"audispd: "),
            FixedDataModelElement("sname_remote", b"audisp-remote: "),
        ])),
        FirstMatchModelElement("msg", [
            ElementValueBranchModelElement("record", SequenceModelElement("preamble", [
                FixedDataModelElement("s0", b"type="),
                WhiteSpaceLimitedDataModelElement("type"),
                FixedDataModelElement("s1", b" msg=audit("),
                DecimalIntegerValueModelElement("time"),
                FixedDataModelElement("s0", b"."),
                DecimalIntegerValueModelElement("ms", value_pad_type=DecimalIntegerValueModelElement.PAD_TYPE_ZERO),
                FixedDataModelElement("s1", b":"),
                DecimalIntegerValueModelElement("seq"),
                FixedDataModelElement("s2", b"):")
            ]), "type", type_branches, default_branch=None),
            FixedDataModelElement("queue-full", b"queue is full - dropping event")
        ])
    ])
    return model
