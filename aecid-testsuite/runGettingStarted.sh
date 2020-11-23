sudo chown -R aminer:aminer /var/lib/aminer 2> /dev/null
sudo aminer --Config demo/AMiner/gettingStarted-config.yml &
sleep 5 & wait $!
sudo pkill -x aminer
exit_code=$?
exit $exit_code
