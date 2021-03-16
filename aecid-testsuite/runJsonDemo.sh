AMINER_PERSISTENCE_PATH=/tmp/lib/aminer/*

sudo mkdir /tmp/lib 2> /dev/null
sudo mkdir /tmp/lib/aminer 2> /dev/null
sudo chown -R $USER:$USER /tmp/lib/aminer 2> /dev/null
sudo rm -r $AMINER_PERSISTENCE_PATH 2> /dev/null
sudo chown -R aminer:aminer /tmp/lib/aminer 2> /dev/null

cp -r ./demo/aminerJsonInputDemo/json_logs /tmp/json_logs

sudo chown -R aminer:aminer /tmp/lib 2> /dev/null
sudo ./demo/aminerJsonInputDemo/json-demo.sh $1 > /tmp/out.txt
exit_code=$?

OUTPUT=$(cat /tmp/out.txt)
if grep -Fq "VerboseUnparsedAtomHandler" /tmp/out.txt; then
	exit_code=1
	sed '/VerboseUnparsedAtomHandler/,$p' /tmp/out.txt
fi

exit $exit_code
sudo rm /tmp/out.txt
sudo rm -r /tmp/json_logs
