#!/bin/bash

test -d aminercfg || mkdir aminercfg
test -d persistency || mkdir persistency
test -d persistency/log || mkdir persistency/log
test -d logs || mkdir logs
test -d akafka || mkdir akafka
test -e aminercfg/config.yml || cp -r source/root/etc/aminer/template_config.yml aminercfg/config.yml
test -d aminercfg/conf-enabled || mkdir aminercfg/conf-enabled
test -e aminercfg/conf-enabled/ApacheAccessModel.py || cp source/root/etc/aminer/conf-available/generic/ApacheAccessModel.py aminercfg/conf-enabled/ApacheAccessModel.py
sed -i "s+#        - 'unix+        - 'unix+g" aminercfg/config.yml
sed -i "s+        - 'file:///var/log/apache2/access.log'+#        - 'file:///logs/access.log'+g" aminercfg/config.yml
sed -i "s+# RemoteControlSocket: '/var/lib/aminer/log/remcontrol.sock'+RemoteControlSocket: '/var/lib/aminer/log/remcontrol.sock'+g" aminercfg/config.yml

