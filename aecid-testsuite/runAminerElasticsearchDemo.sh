cp demo/aminerElasticsearchDemo/elasticsearch-demo-config.yml /tmp/elasticsearch-demo-config.yml
sudo chown -R aminer:aminer /tmp/lib 2> /dev/null
sudo chmod +x demo/aminerElasticsearchDemo/aminerElasticsearchDemo.sh
sudo ./demo/aminer/aminerElasticsearchDemo.sh > /dev/null
exit_code=$?
sudo rm /tmp/elasticsearch-demo-config.yml 2> /dev/null
sudo rm /tmp/syslog
exit $exit_code