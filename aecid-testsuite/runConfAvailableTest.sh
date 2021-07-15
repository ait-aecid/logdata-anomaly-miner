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
            echo '::1 - - [17/May/2015:10:05:03 +0000] "-" 200 203023' > $LOG_FILE
            ;;
        ApacheErrorParsingModel)
            echo "test2" > $LOG_FILE
            ;;
        AuditdParsingModel)
            echo "test3" > $LOG_FILE
            ;;
        EximParsingModel)
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
            echo "test9" > $LOG_FILE
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

    if `grep -Fq "VerboseUnparsedAtomHandler" $OUT` || `grep -Fq "Traceback" $OUT`; then
        echo "Failed Test in $filename"
	    exit_code=1
	    cat $OUT
	    echo
	    echo
    fi
done

rm $CONFIG_PATH
exit $exit_code
