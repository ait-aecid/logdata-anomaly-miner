#!/bin/bash

exit_code=0

CONFIG_PATH=/tmp/config.yml
OUT=/tmp/output.txt
LOG_FILE=/tmp/log.txt
PATH_AIT_LDS=../source/root/etc/aminer/conf-available/ait-lds/*.py
PATH_AIT_LDS=/etc/aminer/conf-available/ait-lds/*.py

for filename in $PATH_AIT_LDS; do
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
        echo "test1" > $LOG_FILE
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
        *)
            echo "Unknown parser config was found! Please extend these tests. Failing.."
            exit_code=2
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

    if grep -Fq "VerboseUnparsedAtomHandler" $OUT; then
    echo "Failed Test in $filename"
	exit_code=1
	sed -ne '/VerboseUnparsedAtomHandler/,$p' $OUT
	echo
	echo
fi
done

rm $CONFIG_PATH
exit $exit_code
