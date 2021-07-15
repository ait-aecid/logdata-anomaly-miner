#!/bin/bash

PATH_AIT_LDS=../source/root/etc/aminer/conf-available/ait-lds/*.py
#PATH_AIT_LDS=/etc/aminer/conf-available/ait-lds/*.py

cat > /tmp/config.py <<EOL
LearnMode: False # optional
Core.PersistenceDir: '/tmp/lib/aminer'

LogResourceList:
        - 'file:///tmp/log.txt'

Input:
        timestamp_paths: ["/accesslog/time"]
        verbose: True # use this to debug your parser-model

EventHandlers:
        - id: stpe
          type: StreamPrinterEventHandler
EOL

for filename in $PATH_AIT_LDS; do
    basename "$filename"
    BN=`basename "$filename"`
    case $BN in
        ApacheAccessParsingModel.py)
            echo True
    esac
done
