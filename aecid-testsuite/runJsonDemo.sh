OUT=/tmp/out.txt
AMINER_PERSISTENCE_PATH=/tmp/lib/aminer/*
sudoInstalled=`dpkg -s sudo | grep Status 2> /dev/null`

if [[ $sudoInstalled == "Status: install ok installed" ]]; then
	sudoInstalled=0
else
	sudoInstalled=1
fi
	
if [[ $sudoInstalled == 0 ]]; then
	sudo mkdir /tmp/lib 2> /dev/null
	sudo mkdir /tmp/lib/aminer 2> /dev/null
	sudo chown -R $USER:$USER /tmp/lib/aminer 2> /dev/null
	sudo rm -r $AMINER_PERSISTENCE_PATH 2> /dev/null
	sudo chown -R aminer:aminer /tmp/lib/aminer 2> /dev/null
else
	mkdir /tmp/lib 2> /dev/null
	mkdir /tmp/lib/aminer 2> /dev/null
	rm -r $AMINER_PERSISTENCE_PATH 2> /dev/null
	chown -R aminer:aminer /tmp/lib/aminer 2> /dev/null
fi

cp -r ./demo/aminerJsonInputDemo/json_logs /tmp/json_logs

sudo chown -R aminer:aminer /tmp/lib 2> /dev/null
sudo ./demo/aminerJsonInputDemo/json-demo.sh $1 > $OUT
exit_code=$?

OUTPUT=$(cat $OUT)
if grep -Fq "VerboseUnparsedAtomHandler" $OUT; then
	exit_code=1
	sed '/VerboseUnparsedAtomHandler/,$p' $OUT
fi

exit $exit_code
sudo rm $OUT
sudo rm -r /tmp/json_logs
