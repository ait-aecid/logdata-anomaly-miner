sudo xsltproc --output /usr/share/man/man1/aminerremotecontrol.1  -''-nonet -''-param man.charmap.use.subset "0" -''-param make.year.ranges "1" -''-param make.single.year.ranges "1" /usr/share/xml/docbook/stylesheet/docbook-xsl/manpages/docbook.xsl /home/user/Documents/Git_projects/logdata-anomaly-miner/debian/aminerremotecontrol.1.xml && sudo gzip /usr/share/man/man1/aminerremotecontrol.1
sudo gunzip /usr/share/man/man1/aminerremotecontrol.1.gz
sudo mv /usr/share/man/man1/aminerremotecontrol.1 /tmp
sudo chown user:user /tmp/aminerremotecontrol.1
sudo apt install pandoc
pandoc --from man --to gfm /tmp/aminerremotecontrol.1 -o /tmp/aminerremotecontrol.md # man-to-github-flawored-markdown
