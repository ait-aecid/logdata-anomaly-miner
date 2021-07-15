#!/bin/bash

exit_code=0

PATH_AIT_LDS=../source/root/etc/aminer/conf-available/ait-lds/*.py
PATH_AIT_LDS=/etc/aminer/conf-available/ait-lds/*.py

for filename in $PATH_AIT_LDS; do
    cat > /tmp/config.yml <<EOL
LearnMode: False
Core.PersistenceDir: '/tmp/lib/aminer'

LogResourceList:
        - 'file:///tmp/log.txt'

Input:
        timestamp_paths: ["/accesslog/time"]
        verbose: True

EventHandlers:
        - id: stpe
          type: StreamPrinterEventHandler

Parser:
        - id: 'testingModel'
EOL

    BN=`basename "$filename"`
    echo "Testing $BN"
    case $BN in
        ApacheAccessParsingModel.py)
            cat >> /tmp/config.yml <<EOL
          type: ApacheAccessModel
          name: 'apache'
          args: 'apache'
EOL
            ;;
        ApacheErrorParsingModel.py)
            echo True
            ;;
        AuditdParsingModel.py)
            echo True
            ;;
        EximParsingModel.py)
            echo True
            ;;
        SuricataEventParsingModel.py)
            echo True
            ;;
        SuricataFastParsingModel.py)
            echo True
            ;;
        SyslogParsingModel.py)
            echo True
            ;;
        *)
            echo "Unknown parser config was found! Please extend these tests. Failing.."
            exit_code=2
            ;;
    esac

    cat >> /tmp/config.yml <<EOL

        - id: 'startModel'
          start: True
          type: SequenceModelElement
          name: 'model'
          args:
            - testingModel
EOL
exit 0
done

exit $exit_code
