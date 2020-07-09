# logdata-anomaly-miner [![Build Status](https://travis-ci.org/ait-aecid/logdata-anomaly-miner.svg?branch=master)](https://travis-ci.org/ait-aecid/logdata-anomaly-miner) [![DeepSource](https://static.deepsource.io/deepsource-badge-light-mini.svg)](https://deepsource.io/gh/ait-aecid/logdata-anomaly-miner/?ref=repository-badge)

This tool allows one to create log analysis pipelines.

# Installation

## Debian

There are Debian packages for logdata-anomaly-miner in the official Debian/Ubuntu
repositories.

```
apt-get update && apt-get install logdata-anomaly-miner
```

## From source

The following command will install the latest stable release:
```
cd $HOME
wget https://raw.githubusercontent.com/ait-aecid/logdata-anomaly-miner/master/scripts/aminer_install.sh
chmod +x aminer_install.sh
./aminer_install.sh
```

## Getting started

Here are some resources to read in order to get started with configurations:

* [Getting started](https://github.com/ait-aecid/logdata-anomaly-miner/wiki/Getting-started-(tutorial))
* [Some available configurations](https://github.com/ait-aecid/logdata-anomaly-miner/tree/master/source/root/etc/aminer/conf-available/generic)
* [Documentation](https://github.com/ait-aecid/logdata-anomaly-miner/tree/master/source/root/usr/share/doc/logdata-anomaly-miner)

## Contribution

We're happily taking patches and other contributions. Please see the following links for how to get started:

* [ How to install a development environment ](https://github.com/ait-aecid/logdata-anomaly-miner/wiki/Installing-a-development-environment)
* [ Git development workflow ](https://github.com/ait-aecid/logdata-anomaly-miner/wiki/Git-development-workflow)

## License

[GPL-3.0](LICENSE)
