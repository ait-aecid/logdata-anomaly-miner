sudo coverage run --source=./aminer -m unittest discover -s unit -p '*Test.py' > /dev/null
touch /tmp/report
echo 'Statement Coverage:' > /tmp/report
sudo coverage report >> /tmp/report
sudo coverage run --source=./aminer --branch -m unittest discover -s unit -p '*Test.py' > /dev/null
echo 'Branch Coverage:' >> /tmp/report
sudo coverage report >> /tmp/report
cat /tmp/report
rm /tmp/report
test -e /var/mail/mail && sudo rm -f /var/mail/mail
sudo rm /tmp/AMinerRemoteLog.txt
sudo rm /tmp/test4unixSocket.sock
sudo rm /tmp/test5unixSocket.sock
sudo rm /tmp/test6unixSocket.sock
