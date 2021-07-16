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
            exit 0
            echo "test4" > $LOG_FILE
            ;;
        SuricataEventParsingModel)
            echo "test5" > $LOG_FILE
            ;;
        SuricataFastParsingModel)
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
