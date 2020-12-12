#
# PLEASE NOTE THAT YOUR WORKING-DIRECTORY MUST BE THE ROOT OF THIS REPOSITORY
# IN ORDER WO BUIILD THIS CONTAINER-IMAGE!!!
#
# Build:
#    docker build -f aecid-testsuite/Dockerfile -t aecid/logdata-anomaly-miner-testing:latest .
#
# Use:
#    docker run -m=2G --rm aecid/logdata-anomaly-miner-testing runUnittests
#
# Run all tests:
#    docker run -m=2G --rm aecid/logdata-anomaly-miner-testing ALL
#
# Run a shell inside the container:
#    docker run -m=2G -it --rm aecid/logdata-anomaly-miner-testing SHELL
#
# See: https://github.com/ait-aecid/logdata-anomaly-miner/wiki/How-to-use-the-AECID-testsuite
#

# Pull base image.
FROM debian:bullseye

# Set local timezone
ENV TZ=Europe/Vienna
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

LABEL maintainer="wolfgang.hotwagner@ait.ac.at"

# Install necessary debian packages
ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y \
	python3 \
	python3-pip \
	python3-pip \
        python3-tz \
        python3-scipy \
        python3-pkg-resources \
        python3-setuptools \
        python3-dateutil \
        python3-six \
        python3-scipy \
        python3-kafka \
        python3-cerberus \
        python3-yaml \
        python3-pylibacl \
        libacl1-dev \
        postfix \
        procps \ 
        mailutils \
        sudo \
        curl \
        postfix \
        openjdk-15-jre \
        locales \
        locales-all \
        rsyslog

RUN sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen && \
    dpkg-reconfigure --frontend=noninteractive locales && \
    update-locale LANG=en_US.UTF-8

ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en  
ENV LC_ALL en_US.UTF-8


RUN pip3 install coverage

# Copy logdata-anomaly-miner-sources
ADD source/root/usr/lib/logdata-anomaly-miner /usr/lib/logdata-anomaly-miner

# Entrypoint-wrapper
ADD scripts/aminerwrapper.sh /aminerwrapper.sh


# Prepare the system and link all python-modules
RUN ln -s /usr/lib/logdata-anomaly-miner/aminerremotecontrol.py /usr/bin/aminerremotecontrol \
	&& ln -s /usr/lib/logdata-anomaly-miner/aminer.py /usr/bin/aminer \
	&& chmod 0755 /usr/lib/logdata-anomaly-miner/aminer.py  \
	&& chmod 0755 /usr/lib/logdata-anomaly-miner/aminerremotecontrol.py \
	&& ln -s /usr/lib/python3/dist-packages/kafka /usr/lib/logdata-anomaly-miner/kafka \
	&& ln -s /usr/lib/python3/dist-packages/cerberus /usr/lib/logdata-anomaly-miner/cerberus \
	&& ln -s /usr/lib/python3/dist-packages/scipy /usr/lib/logdata-anomaly-miner/scipy \
	&& ln -s /usr/lib/python3/dist-packages/numpy /usr/lib/logdata-anomaly-miner/numpy \
	&& ln -s /usr/lib/python3/dist-packages/pkg_resources /usr/lib/logdata-anomaly-miner/pkg_resources \
	&& ln -s /usr/lib/python3/dist-packages/yaml /usr/lib/logdata-anomaly-miner/yaml \
	&& ln -s /usr/lib/python3/dist-packages/pytz /usr/lib/logdata-anomaly-miner/pytz \
	&& ln -s /usr/lib/python3/dist-packages/dateutil /usr/lib/logdata-anomaly-miner/dateutil \
	&& ln -s /usr/lib/python3/dist-packages/six.py /usr/lib/logdata-anomaly-miner/six.py \
	&& useradd -ms /usr/sbin/nologin aminer && mkdir /var/lib/aminer && mkdir /etc/aminer \
        && chmod 0755 /aminerwrapper.sh

RUN PACK=$(find /usr/lib/python3/dist-packages -name posix1e.cpython\*.so) && FILE=$(echo $PACK | awk -F '/' '{print $NF}') ln -s $PACK /usr/lib/logdata-anomaly-miner/$FILE 

# Add config
ADD source/root/etc/aminer /etc/aminer

# Copy the testsuite
ADD aecid-testsuite /home/aminer/aecid-testsuite

RUN chown aminer.aminer -R /home/aminer \
    && ln -s /usr/lib/logdata-anomaly-miner/aminer /home/aminer/aecid-testsuite/aminer \
    && ln -s /etc/aminer/conf-available/generic/ApacheAccessModel.py /etc/aminer/conf-enabled/ApacheAccessModel.py \
    && ln -s /etc/aminer/template_config.py /home/aminer/aecid-testsuite/demo/AMiner/template_config.py \
    && ln -s /etc/aminer/template_config.yml /home/aminer/aecid-testsuite/demo/AMiner/template_config.yml \
    && chmod +x /home/aminer/aecid-testsuite/*.sh \
    && echo "aminer ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/aminer

ADD scripts/testingwrapper.sh /testingwrapper.sh

USER aminer
WORKDIR /home/aminer/aecid-testsuite

# The following volumes can be mounted
VOLUME ["/etc/aminer","/var/lib/aminer","/logs"]

ENTRYPOINT ["/testingwrapper.sh"]
