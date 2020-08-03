#!/bin/bash

#This script should be used as a demo-tool to show different components and their use cases. To show the content just uncomment the needed outputs, which are described in the comment before. 

#
# add the following line to /etc/sudoers.d/<current-user>:
#    <current-user> ALL=(aminer) /pfad/zum/demo.sh
#
# execute demo.sh as aminer:
#    sudo -u aminer /pfad/zum/demo.sh
# 

AMINER_PERSISTENCE_PATH=/tmp/lib/aminer/*
mkdir /tmp/lib 2> /dev/null
mkdir /tmp/lib/aminer 2> /dev/null
# chown -R $USER:$USER /tmp/lib/aminer 2> /dev/null
rm -r $AMINER_PERSISTENCE_PATH 2> /dev/null
# chown -R aminer:aminer /tmp/lib/aminer 2> /dev/null
rm /tmp/syslog 2> /dev/null

echo "Demo started.."
echo ""

FILE=/tmp/demo-config.py
if ! test -f "$FILE"; then
    echo "$FILE does not exist!"
	exit 1
fi

#start AMiner
bash -c 'AMiner --Foreground --Config '$FILE' & #2> /dev/null & #> /tmp/output &'

#EventCorrelationDetetctor, NewMatchPathDetector
#:<<Comment
alphabet='abcdef'
alphabet_len=$(echo -n $alphabet | wc -m)
for ((i=0; i<10000; i++)); do
	echo ${alphabet:$i % $alphabet_len:1} >> /tmp/syslog
	sleep 0.0001
done
#Comment

#EnhancedNewMatchPathValueComboDetector, NewMatchPathValueDetector
#:<<Comment
R=`shuf -i 1-3 -n 1`
for ((i=0; i<R; i++)); do
	R1=`shuf -i 30-50 -n 1`
	R2=`shuf -i 1-65000 -n 1`
	for ((j=0; j<R1; j++)); do
        sleep 0.25
		({ date '+%Y-%m-%d %T' && cat /etc/hostname && id -u -n | tr -d "\n"; } | tr "\n" " " && echo " cron[$R2]: Job \`cron.daily\` started.") >> /tmp/syslog
	done
done
#Comment

#HistogramAnalysis
#:<<Comment
echo "Generating data for the LinearNumericBinDefinition histogram report.."
startTime=`date +%s`
t=`date +%s`
while [[ $t -lt `expr $startTime+11` ]]; do
	R=`shuf -i 0-200 -n 1`
	echo $R >> /tmp/syslog
	t=`date +%s`
done

#PathDependentHistogramAnalysis
sleep 0.5
echo "Generating data for the ModuloTimeBinDefinition histogram report.."
startTime=`date +%s`
t=`date +%s`
while [[ $t -lt `expr $startTime+11` ]]; do
	R=`shuf -i 0-86400 -n 1`
	echo "Random: $R" >> /tmp/syslog
	t=`date +%s`
done
#Comment

#MatchValueAverageChangeDetector
#:<<Comment
startTime=`date +%s`
t=`date +%s`
while [[ $t -lt `expr $startTime+3` ]]; do
	R=`shuf -i 0-200 -n 1`
	echo $R >> /tmp/syslog
	t=`date +%s`
done

startTime=`date +%s`
t=`date +%s`
while [[ $t -lt `expr $startTime+1` ]]; do
	R=`shuf -i 300-1000 -n 1`
	echo $R >> /tmp/syslog
	t=`date +%s`
done
#Comment

#MatchValueStreamWriter
#:<<Comment
startTime=`date +%s`
t=`date +%s`
while [[ $t -lt `expr $startTime+2` ]]; do
	R=`shuf -i 30-85 -n 1`
	R1=`shuf -i 30-85 -n 1`
	({ echo "CPU Temp: $R°C" && echo ", CPU Workload: $R1%, " && date '+%Y-%m-%d %T' | tr -d "\n"; } | tr -d "\n" && echo "") >> /tmp/syslog
	t=`date +%s`
	sleep 0.25
done
#Comment

#MissingMatchPathValueDetector, NewMatchPathDetector
#:<<Comment

#NewMatchPath expected
echo first
echo " Current Disk Data is: Filesystem     Type  Size  Used Avail Use%   %" >> /tmp/syslog
sleep 3

#MissingMatchPathValue expected
echo second
echo " Current Disk Data is: Filesystem     Type  Size  Used Avail Use%   dd%" >> /tmp/syslog
sleep 0.5

#No output expected
echo third
echo " Current Disk Data is: Filesystem     Type  Size  Used Avail Use%   dd%" >> /tmp/syslog
sleep 4

#MissingMatchPathValue expected
echo fourth
echo " Current Disk Data is: Filesystem     Type  Size  Used Avail Use%   dd%" >> /tmp/syslog
#Comment

#NewMatchPathValueComboDetector, NewMatchPathValueDetector
#:<<Comment
startTime=`date +%s`
t=`date +%s`
users=(user root admin guest1 guest2)
while [[ $t -lt `expr $startTime+2` ]]; do
	R=`shuf -i 0-4 -n 1`
	R1=`shuf -i 1-255 -n 1`
	({ echo "User ${users[R]} changed IP address to 10.0.0.$R1" | tr -d "\n"; } | tr -d "\n" && echo "") >> /tmp/syslog
	t=`date +%s`
	sleep 0.25
done
#Comment

#NewMatchIdValueComboDetector
#:<<Comment
echo 'type=SYSCALL msg=audit(1580367384.000:1): arch=c000003e syscall=1 success=yes exit=21 a0=7ffda5863060 a1=0 a2=1b6 a3=4f items=1 ppid=22913 pid=13187 auid=4294967295 uid=33 gid=33 euid=33 suid=33 fsuid=33 egid=33 sgid=33 fsgid=33 tty=(none) ses=4294967295 comm="apache2" exe="/usr/sbin/apache2" key=(null)' >> /tmp/syslog
echo 'type=PATH msg=audit(1580367385.000:1): item=0 name="one" inode=790106 dev=fe:01 mode=0100666 ouid=1000 ogid=1000 rdev=00:00 nametype=NORMAL' >> /tmp/syslog
echo 'type=SYSCALL msg=audit(1580367386.000:2): arch=c000003e syscall=2 success=yes exit=21 a0=7ffda5863060 a1=0 a2=1b6 a3=4f items=1 ppid=22913 pid=13187 auid=4294967295 uid=33 gid=33 euid=33 suid=33 fsuid=33 egid=33 sgid=33 fsgid=33 tty=(none) ses=4294967295 comm="apache2" exe="/usr/sbin/apache2" key=(null)' >> /tmp/syslog
echo 'type=PATH msg=audit(1580367387.000:2): item=0 name="two" inode=790106 dev=fe:01 mode=0100666 ouid=1000 ogid=1000 rdev=00:00 nametype=NORMAL' >> /tmp/syslog
echo 'type=SYSCALL msg=audit(1580367388.000:3): arch=c000003e syscall=3 success=yes exit=21 a0=7ffda5863060 a1=0 a2=1b6 a3=4f items=1 ppid=22913 pid=13187 auid=4294967295 uid=33 gid=33 euid=33 suid=33 fsuid=33 egid=33 sgid=33 fsgid=33 tty=(none) ses=4294967295 comm="apache2" exe="/usr/sbin/apache2" key=(null)' >> /tmp/syslog
echo 'type=PATH msg=audit(1580367389.000:3): item=0 name="three" inode=790106 dev=fe:01 mode=0100666 ouid=1000 ogid=1000 rdev=00:00 nametype=NORMAL' >> /tmp/syslog
echo 'type=SYSCALL msg=audit(1580367388.500:100): arch=c000003e syscall=1 success=yes exit=21 a0=7ffda5863060 a1=0 a2=1b6 a3=4f items=1 ppid=22913 pid=13187 auid=4294967295 uid=33 gid=33 euid=33 suid=33 fsuid=33 egid=33 sgid=33 fsgid=33 tty=(none) ses=4294967295 comm="apache2" exe="/usr/sbin/apache2" key=(null)' >> /tmp/syslog
echo 'type=SYSCALL msg=audit(1580367390.000:4): arch=c000003e syscall=1 success=yes exit=21 a0=7ffda5863060 a1=0 a2=1b6 a3=4f items=1 ppid=22913 pid=13187 auid=4294967295 uid=33 gid=33 euid=33 suid=33 fsuid=33 egid=33 sgid=33 fsgid=33 tty=(none) ses=4294967295 comm="apache2" exe="/usr/sbin/apache2" key=(null)' >> /tmp/syslog
echo 'type=PATH msg=audit(1580367391.000:4): item=0 name="one" inode=790106 dev=fe:01 mode=0100666 ouid=1000 ogid=1000 rdev=00:00 nametype=NORMAL' >> /tmp/syslog
echo 'type=PATH msg=audit(1580367392.000:5): item=0 name="two" inode=790106 dev=fe:01 mode=0100666 ouid=1000 ogid=1000 rdev=00:00 nametype=NORMAL' >> /tmp/syslog
echo 'type=SYSCALL msg=audit(1580367393.000:5): arch=c000003e syscall=2 success=yes exit=21 a0=7ffda5863060 a1=0 a2=1b6 a3=4f items=1 ppid=22913 pid=13187 auid=4294967295 uid=33 gid=33 euid=33 suid=33 fsuid=33 egid=33 sgid=33 fsgid=33 tty=(none) ses=4294967295 comm="apache2" exe="/usr/sbin/apache2" key=(null)' >> /tmp/syslog
echo 'type=SYSCALL msg=audit(1580367394.000:6): arch=c000003e syscall=4 success=yes exit=21 a0=7ffda5863060 a1=0 a2=1b6 a3=4f items=1 ppid=22913 pid=13187 auid=4294967295 uid=33 gid=33 euid=33 suid=33 fsuid=33 egid=33 sgid=33 fsgid=33 tty=(none) ses=4294967295 comm="apache2" exe="/usr/sbin/apache2" key=(null)' >> /tmp/syslog
echo 'type=PATH msg=audit(1580367395.000:7): item=0 name="five" inode=790106 dev=fe:01 mode=0100666 ouid=1000 ogid=1000 rdev=00:00 nametype=NORMAL' >> /tmp/syslog
echo 'type=SYSCALL msg=audit(1580367396.000:8): arch=c000003e syscall=6 success=yes exit=21 a0=7ffda5863060 a1=0 a2=1b6 a3=4f items=1 ppid=22913 pid=13187 auid=4294967295 uid=33 gid=33 euid=33 suid=33 fsuid=33 egid=33 sgid=33 fsgid=33 tty=(none) ses=4294967295 comm="apache2" exe="/usr/sbin/apache2" key=(null)' >> /tmp/syslog
echo 'type=PATH msg=audit(1580367397.000:6): item=0 name="four" inode=790106 dev=fe:01 mode=0100666 ouid=1000 ogid=1000 rdev=00:00 nametype=NORMAL' >> /tmp/syslog
echo 'type=SYSCALL msg=audit(1580367398.000:7): arch=c000003e syscall=5 success=yes exit=21 a0=7ffda5863060 a1=0 a2=1b6 a3=4f items=1 ppid=22913 pid=13187 auid=4294967295 uid=33 gid=33 euid=33 suid=33 fsuid=33 egid=33 sgid=33 fsgid=33 tty=(none) ses=4294967295 comm="apache2" exe="/usr/sbin/apache2" key=(null)' >> /tmp/syslog
echo 'type=PATH msg=audit(1580367399.000:8): item=0 name="six" inode=790106 dev=fe:01 mode=0100666 ouid=1000 ogid=1000 rdev=00:00 nametype=NORMAL' >> /tmp/syslog
echo 'type=SYSCALL msg=audit(1580367400.000:9): arch=c000003e syscall=2 success=yes exit=21 a0=7ffda5863060 a1=0 a2=1b6 a3=4f items=1 ppid=22913 pid=13187 auid=4294967295 uid=33 gid=33 euid=33 suid=33 fsuid=33 egid=33 sgid=33 fsgid=33 tty=(none) ses=4294967295 comm="apache2" exe="/usr/sbin/apache2" key=(null)' >> /tmp/syslog
echo 'type=PATH msg=audit(1580367401.000:9): item=0 name="three" inode=790106 dev=fe:01 mode=0100666 ouid=1000 ogid=1000 rdev=00:00 nametype=NORMAL' >> /tmp/syslog
echo 'type=PATH msg=audit(1580367402.000:10): item=0 name="one" inode=790106 dev=fe:01 mode=0100666 ouid=1000 ogid=1000 rdev=00:00 nametype=NORMAL' >> /tmp/syslog
echo 'type=SYSCALL msg=audit(1580367403.000:10): arch=c000003e syscall=3 success=yes exit=21 a0=7ffda5863060 a1=0 a2=1b6 a3=4f items=1 ppid=22913 pid=13187 auid=4294967295 uid=33 gid=33 euid=33 suid=33 fsuid=33 egid=33 sgid=33 fsgid=33 tty=(none) ses=4294967295 comm="apache2" exe="/usr/sbin/apache2" key=(null)' >> /tmp/syslog
#Comment

#TimeCorrelationDetector
#At least 3000 lines must be passed to trigger the TimeCorrelationDetector.


#TimeCorrelationViolationDetector
#The input text is saying that the time between cron job announcement and execution is 5 minutes, but in reality it is 5 seconds for more convenience.

#:<<Comment
#too short time difference
({ date '+%Y-%m-%d %T ' && cat /etc/hostname && echo " cron[50000]: Will run job \`cron.daily' in 5 min." | tr -d "\n"; } | tr -d "\n" && echo "") >> /tmp/syslog
sleep 4
({ date '+%Y-%m-%d %T ' && cat /etc/hostname && echo " cron[50000]: Job \`cron.daily' started" | tr -d "\n"; } | tr -d "\n" && echo "") >> /tmp/syslog
sleep 10

#wrong Job Number
({ date '+%Y-%m-%d %T ' && cat /etc/hostname && echo " cron[50000]: Will run job \`cron.daily' in 5 min." | tr -d "\n"; } | tr -d "\n" && echo "") >> /tmp/syslog
sleep 5
({ date '+%Y-%m-%d %T ' && cat /etc/hostname && echo " cron[50001]: Job \`cron.daily' started" | tr -d "\n"; } | tr -d "\n" && echo "") >> /tmp/syslog
sleep 10

#expected time difference
({ date '+%Y-%m-%d %T ' && cat /etc/hostname && echo " cron[50000]: Will run job \`cron.daily' in 5 min." | tr -d "\n"; } | tr -d "\n" && echo "") >> /tmp/syslog
sleep 5
({ date '+%Y-%m-%d %T ' && cat /etc/hostname && echo " cron[50000]: Job \`cron.daily' started" | tr -d "\n"; } | tr -d "\n" && echo "") >> /tmp/syslog
sleep 10

#too long time difference
({ date '+%Y-%m-%d %T ' && cat /etc/hostname && echo " cron[50000]: Will run job \`cron.daily' in 5 min." | tr -d "\n"; } | tr -d "\n" && echo "") >> /tmp/syslog
sleep 7
({ date '+%Y-%m-%d %T ' && cat /etc/hostname && echo " cron[50000]: Job \`cron.daily' started" | tr -d "\n"; } | tr -d "\n" && echo "") >> /tmp/syslog
sleep 10

#Comment

# WhitelistRules, WhitelistViolationDetector
#:<<Comment
echo "User username logged in" >> /tmp/syslog
echo "User root logged in" >> /tmp/syslog
who | awk '{print $1,$3,$4}' | while read user time; do \
  echo User $user logged in $(($(($(date +%s) - $(date -d "$time" +%s)))/60)) minutes ago.>> /tmp/syslog
  echo User root logged in $(($(($(date +%s) - $(date -d "$time" +%s)))/60)) minutes ago. >> /tmp/syslog; done 
#Comment

#:<<Comment
# Unparsed Atom
({ date '+%Y-%m-%d %T' && cat /etc/hostname && id -u -n | tr -d "\n"; } | tr "\n" " " && echo " cron[123]: Job \`cron.daily\`") >> /tmp/syslog
# AnyByteDataModelElement
echo "Any:dafsdff12%3§fasß?–_=yy" >> /tmp/syslog
# Base64StringModelElement
echo "VXNlcm5hbWU6ICJ1c2VyIgpQYXNzd29yZDogInBhc3N3b3JkIg==" >> /tmp/syslog
# DateTimeModelElement
({ echo "Current DateTime: " && date '+%d.%m.%Y %T' | tr -d "\n"; } | tr -d "\n" && echo "") >> /tmp/syslog
# DecimalFloatValueModelElement
echo "-25878952156245.222239655488955" >> /tmp/syslog
# DecimalIntegerValueModelElement
echo "- 3695465546654" >> /tmp/syslog
# DelimitedDataModelElement
echo "This is some part of a csv file;" >> /tmp/syslog
# ElementValueBranchModelElement
echo "match data: 25000" >> /tmp/syslog
# HexStringModelElement
echo "b654686973206973206a7573742061206e6f726d616c2074657874" >> /tmp/syslog
# IpAddressModelElement
echo "Gateway IP-Address: 192.168.128.225" >> /tmp/syslog
# MultiLocaleDateTimeModelElement
echo "Feb 25 2019" >> /tmp/syslog
# OptionalMatchModelElement
echo "The-searched-element-was-found!" >> /tmp/syslog
# RepeatedElementDataModelElement
for i in {1..5}; do
	R=`shuf -i 1-45 -n 1`
	echo "drawn number: $R" | tr -d "\n" >> /tmp/syslog
done
echo "" >> /tmp/syslog
# VariableByteDataModelElement
echo "---------------------------------------------------------------------" >> /tmp/syslog
# WhiteSpaceLimitedDataModelElement
alphabet="abcdefghijklmnopqrstuvwxyz "
text=""
for i in {1..1000}; do
	R=`shuf -i 0-26 -n 1`
	text=$text${alphabet:R:1}
	if [ $R -eq 26 ]; then
		break
	fi
done
echo "$text" >> /tmp/syslog
#Comment

#stop AMiner
sleep 3 & wait $!
pkill AMiner
KILL_PID=$!
sleep 3
wait $KILL_PID
