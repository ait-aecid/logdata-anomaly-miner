cp demo/aminerElasticsearchDemo/elasticsearch-demo-config.yml /tmp/json-input-demo-config.yml
sudo chown -R aminer:aminer /tmp/lib 2> /dev/null
sudo chmod +x demo/aminerJsonInputDemo/aminerJsonInputDemo.sh
sudo ./demo/aminerJsonInputDemo/aminerJsonInputDemo.sh > /dev/null
exit_code=$?
sudo rm /tmp/json-input-demo-config.yml 2> /dev/null
sudo rm /tmp/syslog
exit $exit_code
