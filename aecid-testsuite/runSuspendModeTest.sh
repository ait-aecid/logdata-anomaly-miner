sudo cp demo/AMinerRemoteControl/demo-config.py /tmp/demo-config.py
sudo chown aminer:aminer /tmp/demo-config.py 2> /dev/null
sudo chown -R aminer:aminer /tmp/lib 2> /dev/null
sudo mkdir /tmp/lib 2> /dev/null
sudo mkdir /tmp/lib/aminer 2> /dev/null
sudo rm -r $AMINER_PERSISTENCE_PATH 2> /dev/null
sudo chown -R aminer:aminer /tmp/lib/aminer 2> /dev/null
sudo rm /tmp/syslog 2> /dev/null
touch /tmp/syslog
ln -s $PWD/../source/root/usr/lib/logdata-anomaly-miner/aminer $PWD/aminer
ln -s $PWD/../source/root/usr/lib/logdata-anomaly-miner/aminerRemoteControl.py $PWD/aminerRemoteControl

FILE=/tmp/demo-config.py
if ! test -f "$FILE"; then
    echo "$FILE does not exist!"
	exit 1
fi

exit_code=0
SUSPEND_FILE=/tmp/suspend_output.txt
SUSPEND_FILE_MD5=/tmp/suspend.md5

sudo aminer --Foreground --Config $FILE > $SUSPEND_FILE &

sleep 3

md5sum $SUSPEND_FILE > $SUSPEND_FILE_MD5 2> /dev/null
echo test_logline1 >> /tmp/syslog
sleep 1
md5_result=`md5sum -c $SUSPEND_FILE_MD5 2> /dev/null`
if [[ $md5_result == "$SUSPEND_FILE: OK" ]]; then
	echo 'The aminer should have produced outputs, but md5sum does not indicate any changes. (1)'
	exit_code=1
fi

md5sum $SUSPEND_FILE > $SUSPEND_FILE_MD5 2> /dev/null
sudo ./aminerRemoteControl --Exec "suspend" > /dev/null
echo test_logline2 >> /tmp/syslog
md5_result=`md5sum -c $SUSPEND_FILE_MD5 2> /dev/null`
if [[ $md5_result != "$SUSPEND_FILE: OK" ]]; then
	echo 'The aminer has produced outputs after being suspended.'
	exit_code=1
fi

sudo ./aminerRemoteControl --Exec "activate" > /dev/null

if [[ $md5_result == "/tmp/syslog: OK" ]]; then
	echo 'The aminer should have produced outputs, but md5sum does not indicate any changes. (2)'
	exit_code=1
fi

sudo pkill -x aminer
KILL_PID=$!
sleep 3
wait $KILL_PID

sudo rm /tmp/demo-config.py 2> /dev/null
sudo rm /tmp/suspend_output.txt 2> /dev/null
sudo rm /tmp/syslog 2> /dev/null
sudo rm /tmp/AMinerRemoteLog.txt 2> /dev/null
sudo rm /tmp/suspend.md5 2> /dev/null
sudo rm aminer
sudo rm aminerRemoteControl

exit $exit_code
