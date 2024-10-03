#!/bin/bash

cd /usr/share/man/man1/
sudo xsltproc --output /usr/share/man/man1/aminerremotecontrol.1  -''-nonet -''-param man.charmap.use.subset "0" -''-param make.year.ranges "1" -''-param make.single.year.ranges "1" /usr/share/xml/docbook/stylesheet/docbook-xsl/manpages/docbook.xsl /home/user/Documents/Git_projects/logdata-anomaly-miner/docs/manpages/aminerremotecontrol.1.xml && sudo gzip /usr/share/man/man1/aminerremotecontrol.1
sudo gunzip /usr/share/man/man1/aminerremotecontrol.1.gz
sudo cp /usr/share/man/man1/aminerremotecontrol.1 /tmp
sudo chown user:user /tmp/aminerremotecontrol.1
sudo apt install pandoc
pandoc --from man --to gfm /tmp/aminerremotecontrol.1 -o /tmp/aminerremotecontrol.md # man-to-github-flawored-markdown
# quotes are not successfully recreated from the parser..
sed -i $'s/,property\\\_name/,\'property\\\_name\'/g' /tmp/aminerremotecontrol.md
sed -i $'s/,attribute/,\'attribute\'/g' /tmp/aminerremotecontrol.md
sed -i $'s/NewMatchPath,/\'NewMatchPath\',/g' /tmp/aminerremotecontrol.md
sed -i $'s/NewMatchPathDet)/\'NewMatchPathDet\')/g' /tmp/aminerremotecontrol.md
sed -i $'s/auto\\\_include\\\_flag,/\'auto\\\_include\\\_flag\',/g' /tmp/aminerremotecontrol.md
sed -i $'s/auto\\\_include\\\_flag)/\'auto\\\_include\\\_flag\')/g' /tmp/aminerremotecontrol.md
sed -i $'s/,old\\\_component\\\_name,/,\'old\\\_component\\\_name\',/g' /tmp/aminerremotecontrol.md
sed -i $'s/,new\\\_component\\\_name/,\'new\\\_component\\\_name\'/g' /tmp/aminerremotecontrol.md
sed -i $'s/,history\\\_component\\\_name/,\'history\\\_component\\\_name\'/g' /tmp/aminerremotecontrol.md
sed -i $'s/NewMatchPathDetector/\'NewMatchPathDetector\'/g' /tmp/aminerremotecontrol.md
sed -i $'s/\*\'NewMatchPathDetector\'\*/\*NewMatchPathDetector\*/g' /tmp/aminerremotecontrol.md
sed -i $'s/,component\\\_name/,\'component\\\_name\'/g' /tmp/aminerremotecontrol.md
sed -i $'s/AtomFilter/,\'AtomFilter\'/g' /tmp/aminerremotecontrol.md
sed -i $'s/LogResourceList/\'LogResourceList\'/g' /tmp/aminerremotecontrol.md
sed -i $'s/,atom\\\_handler,/,\'atom\\\_handler\',/g' /tmp/aminerremotecontrol.md
sed -i $'s/,destination\\\_file/,\'destination\\\_file\'/g' /tmp/aminerremotecontrol.md
sed -i $'s,/tmp/config.py,\'/tmp/config.py\',g' /tmp/aminerremotecontrol.md
sed -i $'s/,EnhancedNewMatchPathValueComboDetector,/,\'EnhancedNewMatchPathValueComboDetector\',/g' /tmp/aminerremotecontrol.md
sed -i $'s/,MissingMatchPathValueDetector,/,\'MissingMatchPathValueDetector\',/g' /tmp/aminerremotecontrol.md
sed -i $'s/,NewMatchPathValueComboDetector,/,\'NewMatchPathValueComboDetector\',/g' /tmp/aminerremotecontrol.md
sed -i $'s,new/path,\'new/path\',g' /tmp/aminerremotecontrol.md
sed -i $'s/,VolatileLogarithmicBackoffEventHistory,/,\'VolatileLogarithmicBackoffEventHistory\',/g' /tmp/aminerremotecontrol.md
sed -i $'s/,MailAlerting.TargetAddress,/,\'MailAlerting.TargetAddress\',/g' /tmp/aminerremotecontrol.md
sed -i $'s/root@localhost/\'root@localhost\'/g' /tmp/aminerremotecontrol.md
sed -i $'s/,MailAlerting.FromAddress,/,\'MailAlerting.FromAddress\',/g' /tmp/aminerremotecontrol.md
sed -i $'s/,MailAlerting.SubjectPrefix,/,\'MailAlerting.SubjectPrefix\',/g' /tmp/aminerremotecontrol.md
sed -i $'s/aminer Alerts:)/\'aminer Alerts:\')/g' /tmp/aminerremotecontrol.md
sed -i $'s/,MailAlerting.EventCollectTime,/,\'MailAlerting.EventCollectTime\',/g' /tmp/aminerremotecontrol.md
sed -i $'s/,MailAlerting.MinAlertGap,/,\'MailAlerting.MinAlertGap\',/g' /tmp/aminerremotecontrol.md
sed -i $'s/,MailAlerting.MaxAlertGap,/,\'MailAlerting.MaxAlertGap\',/g' /tmp/aminerremotecontrol.md
sed -i $'s/,MailAlerting.MaxEventsPerMessage,/,\'MailAlerting.MaxEventsPerMessage\',/g' /tmp/aminerremotecontrol.md
sed -i $'s/,LogPrefix,/,\'LogPrefix\',/g' /tmp/aminerremotecontrol.md
sed -i $'s/Original log/\'Original log/g' /tmp/aminerremotecontrol.md
sed -i $'s/line: /line: \'/g' /tmp/aminerremotecontrol.md
sed -i $'s/This defaults to ./This defaults to \'\'./g' /tmp/aminerremotecontrol.md
sed -i $'s/,Resources.MaxMemoryUsage,/,\'Resources.MaxMemoryUsage\',/g' /tmp/aminerremotecontrol.md
sed -i $'s/,Core.PersistencePeriod,/,\'Core.PersistencePeriod\',/g' /tmp/aminerremotecontrol.md
sed -i $'s/,Log.StatisticsLevel,/,\'Log.StatisticsLevel\',/g' /tmp/aminerremotecontrol.md
sed -i $'s/,Log.DebugLevel,/,\'Log.DebugLevel\',/g' /tmp/aminerremotecontrol.md
sed -i $'s/,Log.StatisticsPeriod,/,\'Log.StatisticsPeriod\',/g' /tmp/aminerremotecontrol.md
sed -i $'s/\*\*\*socket/\*\* \*socket/g' /tmp/aminerremotecontrol.md
sed -i $'s/\*\*\*command/\*\* \*command/g' /tmp/aminerremotecontrol.md
sed -i $'s/\*\*\*file/\*\* \*file/g' /tmp/aminerremotecontrol.md
sed -i $'s/\*\*\*data/\*\* \*data/g' /tmp/aminerremotecontrol.md
sed -i $'s/command\*\*\*/command\* \*\*/g' /tmp/aminerremotecontrol.md
sed -i $'s/file\*\*\*/file\* \*\*/g' /tmp/aminerremotecontrol.md
sed -i $'s/^\*\*$//g' /tmp/aminerremotecontrol.md
sed -i $'s/^\*\* \*\*\*/\*\*\*/g' /tmp/aminerremotecontrol.md
sed -i $'s/\*\*\* \*\*/\*\*\*/g' /tmp/aminerremotecontrol.md
sed -i $'s/\*\*\*/\*\*/g' /tmp/aminerremotecontrol.md
sed -i ':a;N;$!ba;s/\*\*aminerremotecontrol\*\* \\\[\*\*\\\[--exec \*\* \*command\* \*\*\\] | \\\[--exec-file\n\*\* \*file\* \*\*\\]\*\*\\] \*\*\\\[OPTIONS\\]...\*\*/\*\*aminerremotecontrol\*\* \\\[\*\*\\\[--exec \*\* \*command\* \*\*\\] | \\\[--exec-file\*\* \*file\* \*\*\\]\*\*\\] \*\*\\\[OPTIONS\\]...\*\*/g' /tmp/aminerremotecontrol.md
