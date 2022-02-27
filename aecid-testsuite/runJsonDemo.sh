OUT=/tmp/out.txt
AMINER_PERSISTENCE_PATH=/tmp/lib/aminer/*

sudo mkdir /tmp/lib 2> /dev/null
sudo mkdir /tmp/lib/aminer 2> /dev/null
sudo chown -R $USER:$USER /tmp/lib/aminer 2> /dev/null
sudo rm -r $AMINER_PERSISTENCE_PATH 2> /dev/null
sudo chown -R aminer:aminer /tmp/lib/aminer 2> /dev/null

cp -r ./demo/aminerJsonInputDemo/json_logs /tmp/json_logs
cp -r ./demo/aminerJsonInputDemo/windows_json_logs /tmp/windows_json_logs

sudo chown -R aminer:aminer /tmp/lib 2> /dev/null
sudo ./demo/aminerJsonInputDemo/json-demo.sh $1 > $OUT
exit_code=$?

OUTPUT=$(cat $OUT)
if grep -Fq "VerboseUnparsedAtomHandler" $OUT; then
	exit_code=1
	sed '/VerboseUnparsedAtomHandler/,$p' $OUT
fi

if grep -Fq "UnicodeDecodeError" $OUT || grep -Fq "Config-Error" $OUT || grep -Fq "Traceback" $OUT; then
	exit_code=1
	sed '/UnicodeDecodeError/,$p' $OUT
	sed '/Config-Error/,$p' $OUT
	sed '/Traceback/,$p' $OUT
fi

sudo rm $OUT
sudo rm -r /tmp/json_logs
sudo rm -r /tmp/windows_json_logs
exit $exit_code
