sudo cp demo/aminerRemoteControl/demo-config.py /tmp/demo-config.py
echo "config_properties['Core.PersistencePeriod'] = 15" | sudo tee -a /tmp/demo-config.py > /dev/null
sudo chown aminer:aminer /tmp/demo-config.py 2> /dev/null
sudo rm -r /tmp/lib/aminer/* 2> /dev/null
sudo mkdir /tmp/lib 2> /dev/null
sudo mkdir /tmp/lib/aminer 2> /dev/null
sudo mkdir /tmp/lib/aminer/log 2> /dev/null
sudo chown -R aminer:aminer /tmp/lib 2> /dev/null
sudo rm /tmp/syslog 2> /dev/null
touch /tmp/syslog
ln -s $PWD/../source/root/usr/lib/logdata-anomaly-miner/aminerremotecontrol.py $PWD/aminerremotecontrol

FILE=/tmp/demo-config.py
if ! test -f "$FILE"; then
    echo "$FILE does not exist!"
	exit 1
fi

exit_code=0
SUSPEND_FILE=/tmp/suspend_output.txt
SUSPEND_FILE_MD5=/tmp/suspend.md5

sudo aminer --config "$FILE" > $SUSPEND_FILE &
PID=$!

for i in {1..60}; do grep "INFO aminer started." /tmp/lib/aminer/log/aminer.log > /dev/null 2>&1; if [[ $? == 0 ]]; then break; fi; sleep 1; done
md5sum $SUSPEND_FILE > $SUSPEND_FILE_MD5 2> /dev/null

echo "User username logged in" >> /tmp/syslog
for i in {1..60}; do grep "Original log line: User username logged in" $SUSPEND_FILE > /dev/null 2>&1; if [[ $? == 0 ]]; then break; fi; sleep 1; done

md5_result=`md5sum -c $SUSPEND_FILE_MD5 2> /dev/null`
if [[ $md5_result == "$SUSPEND_FILE: OK" ]]; then
	echo 'The aminer should have produced outputs, but md5sum does not indicate any changes. (1)'
	exit_code=1
fi

find /tmp/lib/aminer -type f ! -path "/tmp/lib/aminer/log/aminerRemoteLog.txt" ! -path "/tmp/lib/aminer/log/aminer.log" ! -path "/tmp/lib/aminer/log/statistics.log" -exec md5sum {} \; | tee /tmp/test1.md5 > /dev/null

md5sum $SUSPEND_FILE > $SUSPEND_FILE_MD5 2> /dev/null
sudo aminerremotecontrol --exec "suspend" > /dev/null
echo " Current Disk Data is: Filesystem     Type  Size  Used Avail Use%   %" >> /tmp/syslog
sleep 20
md5_result=`md5sum -c $SUSPEND_FILE_MD5 2> /dev/null`
if [[ $md5_result != "$SUSPEND_FILE: OK" ]]; then
	echo 'The aminer has produced outputs after being suspended.'
	exit_code=1
fi

find /tmp/lib/aminer -type f ! -path "/tmp/lib/aminer/log/aminerRemoteLog.txt" ! -path "/tmp/lib/aminer/log/aminer.log" ! -path "/tmp/lib/aminer/log/statistics.log" -exec md5sum {} \; | tee /tmp/test2.md5 > /dev/null

sudo aminerremotecontrol --exec "activate" > /dev/null
for i in {1..60}; do grep "Original log line:  Current Disk Data is: Filesystem     Type  Size  Used Avail Use%   %" $SUSPEND_FILE > /dev/null 2>&1; if [[ $? == 0 ]]; then break; fi; sleep 1; done

if [[ $md5_result == "/tmp/syslog: OK" ]]; then
	echo 'The aminer should have produced outputs, but md5sum does not indicate any changes. (2)'
	exit_code=1
fi

for i in {1..60}; do test -f /tmp/lib/aminer/AnalysisChild/RepositioningData; if [[ $? == 0 ]]; then break; fi; sleep 1; done

find /tmp/lib/aminer -type f ! -path "/tmp/lib/aminer/log/aminerRemoteLog.txt" ! -path "/tmp/lib/aminer/log/aminer.log" ! -path "/tmp/lib/aminer/log/statistics.log" -exec md5sum {} \; | tee /tmp/test3.md5 > /dev/null

suspend_diff=`diff /tmp/test1.md5 /tmp/test2.md5`
activate_diff=`diff /tmp/test2.md5 /tmp/test3.md5`

if [[ $suspend_diff != "" ]]; then
  cat /tmp/test1.md5
  cat /tmp/test2.md5
	echo 'The aminer should not persist data after being suspended.'
	exit_code=1
fi

if [[ $activate_diff == "" ]]; then
  cat /tmp/test2.md5
  cat /tmp/test3.md5
	echo 'The aminer should persist data after being activated.'
	exit_code=1
fi

sudo pkill -x aminer
sleep 3
wait $PID
if [[ $? != 0 ]]; then
	exit_code=1
fi

sudo rm /tmp/demo-config.py
sudo rm /tmp/suspend_output.txt
sudo rm /tmp/syslog
sudo rm -r /tmp/lib/aminer/* 2> /dev/null
sudo rm /tmp/suspend.md5
sudo rm aminerremotecontrol
sudo rm /tmp/test1.md5
sudo rm /tmp/test2.md5
sudo rm /tmp/test3.md5
test -e /var/mail/mail && sudo rm -f /var/mail/mail

exit $exit_code
