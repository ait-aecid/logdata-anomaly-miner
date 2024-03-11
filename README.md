# logdata-anomaly-miner [![Build Status](https://aecidjenkins.ait.ac.at/buildStatus/icon?job=AECID%2FAECID%2Flogdata-anomaly-miner%2Fmain)]( "https://aecidjenkins.ait.ac.at/job/AECID/job/AECID/job/logdata-anomaly-miner/job/main/") [![DeepSource](https://static.deepsource.io/deepsource-badge-light-mini.svg)](https://deepsource.io/gh/ait-aecid/logdata-anomaly-miner/?ref=repository-badge)

This tool parses log data and allows to define analysis pipelines for anomaly detection. It was designed to run the analysis with limited resources and lowest possible permissions to make it suitable for production server use.

[![AECID Demo – Anomaly Detection with aminer and Reporting to IBM QRadar](https://img.youtube.com/vi/tL7KiMf8NfE/0.jpg)](https://www.youtube.com/watch?v=tL7KiMf8NfE)

## Requirements

In order to install logdata-anomaly-miner a **Linux system** with **python >= 3.6** is required. **Debian-based** distributions are currently recommended, but also **Fedora** and **RedHat** are supported.

_See [requirements.txt](https://github.com/ait-aecid/logdata-anomaly-miner/requirements.txt) for further module dependencies_


## Installation

### Debian

There are Debian packages for logdata-anomaly-miner in the official Debian/Ubuntu repositories.

```
apt-get update && apt-get install logdata-anomaly-miner
```

### From source

The following command will install the latest stable release:
```
cd $HOME
wget https://raw.githubusercontent.com/ait-aecid/logdata-anomaly-miner/main/scripts/aminer_install.sh
chmod +x aminer_install.sh
./aminer_install.sh
```

### Docker

For installation with Docker see: [Deployment with Docker](https://github.com/ait-aecid/logdata-anomaly-miner/wiki/Deployment-with-Docker)

## Getting started

Here are some resources to read in order to get started with configurations:

* [Getting started](https://github.com/ait-aecid/logdata-anomaly-miner/wiki/Getting-started-(tutorial))
* [Some available configurations](https://github.com/ait-aecid/logdata-anomaly-miner/tree/main/source/root/etc/aminer/)
* [Documentation](https://aeciddocs.ait.ac.at/logdata-anomaly-miner/)
* [Wiki](https://github.com/ait-aecid/logdata-anomaly-miner/wiki)

## Publications

Publications and talks:

* Landauer M., Wurzenberger M., Skopik F., Hotwagner W., Höld G. (2023): [AMiner: A Modular Log Data Analysis Pipeline for Anomaly-based Intrusion Detection](https://dl.acm.org/doi/full/10.1145/3567675). [Digital Threats: Research and Practice](https://dl.acm.org/toc/dtrap/2023/4/1), Volume 4, Issue 1. March 2023, pp. 1–16, ACM. \[[PDF](https://dl.acm.org/doi/pdf/10.1145/3567675)\]
* Wurzenberger M., Skopik F., Settanni G., Fiedler R. (2018): [AECID: A Self-learning Anomaly Detection Approach Based on Light-weight Log Parser Models](http://www.scitepress.org/DigitalLibrary/Link.aspx?doi=10.5220/0006643003860397). [4th International Conference on Information Systems Security and Privacy (ICISSP 2018)](http://www.icissp.org/), January 22-24, 2018, Funchal, Madeira - Portugal. INSTICC. \[[PDF](https://pdfs.semanticscholar.org/cd58/8e51d7a1d7f02f95ef2127623b21e2cd02c6.pdf)\]
* Wurzenberger M., Landauer M., Skopik F., Kastner W. (2019): AECID-PG: [AECID-PG: A Tree-Based Log Parser Generator To Enable Log Analysis](https://ieeexplore.ieee.org/document/8717887). [4th IEEE/IFIP International Workshop on Analytics for Network and Service Management (AnNet 2019)](https://annet2019.moogsoft.com/) in conjunction with the [IFIP/IEEE International Symposium on Integrated Network Management (IM)](https://im2019.ieee-im.org/), April 8, 2019, Washington D.C., USA. IEEE. \[[PDF](https://ieeexplore.ieee.org/stamp/stamp.jsp?arnumber=8717887)\]
* Landauer M., Skopik F., Wurzenberger M., Hotwagner W., Rauber A. (2019): [A Framework for Cyber Threat Intelligence Extraction from Raw Log Data](https://ieeexplore.ieee.org/document/9006328). [International Workshop on Big Data Analytics for Cyber Threat Hunting (CyberHunt 2019)](https://securitylab.no/cyberhunt2019/) in conjunction with the [IEEE International Conference on Big Data 2019](http://bigdataieee.org/BigData2019/), December 9-12, 2019, Los Angeles, CA, USA. IEEE. \[[PDF](https://ieeexplore.ieee.org/stamp/stamp.jsp?arnumber=9006328)\]

A complete list of publications can be found at [https://aecid.ait.ac.at/further-information/](https://aecid.ait.ac.at/further-information/).


## Contribution

We're happily taking patches and other contributions. Please see the following links for how to get started:

* [ How to install a development environment ](https://github.com/ait-aecid/logdata-anomaly-miner/wiki/Installing-a-development-environment)
* [ Git development workflow ](https://github.com/ait-aecid/logdata-anomaly-miner/wiki/Git-development-workflow)

## Bugs

If you encounter any bugs, please create an issue on [Github](https://github.com/ait-aecid/logdata-anomaly-miner/issues).

## Security

If you discover any security-related issues read the [SECURITY.md](/SECURITY.md) first and report the issues.

## License

[GPL-3.0](LICENSE)

## Financial Support
This project received financial support through the research projects CAIS (832345), CIIS (840842), and CISA (850199) in course of the Austrian KIRAS security research programme, the research projects synERGY (855457) and DECEPT (873980) in course of the ICT of the future programme of the Austrian Research Promotion Agency (FFG), the research project PANDORA (SI2.835928) in course of the European Defence Industrial Development Programme (EDIDP), as well as the research projects ECOSSIAN (607577) and GUARD (833456) in course of the European Seventh Framework Programme (FP7) and Horizon 2020.
