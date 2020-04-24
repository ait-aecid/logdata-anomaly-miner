cd integration
script=$1
sudo chmod +x $script
cntr=0

for var in "$@"
do
	if [[ $cntr -gt 0 ]]; then
    	cp "$var" /tmp/"$var"
		sudo chown aminer:aminer /tmp/"$var"
	fi
	cntr=$(($cntr+1))
done

sudo ./$script

cntr=0
for var in "$@"
do
	if [[ $cntr -gt 0 ]]; then
    	sudo rm /tmp/"$var"
	fi
	cntr=$(($cntr+1))
done

echo mail
test -e /var/mail/mail && sudo rm -f /var/mail/mail
cd ..
echo "rm"
sudo rm /tmp/AMinerRemoteLog.txt
sudo rm /tmp/syslog
sudo rm /tmp/output
test -e /tmp/out && sudo rm /tmp/out
test -e /tmp/auth.log && sudo rm /tmp/auth.log
