#
# PLEASE NOTE THAT YOUR WORKING-DIRECTORY MUST BE THE ROOT OF THIS REPOSITORY
# IN ORDER WO BUILD THIS CONTAINER-IMAGE!!!
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
FROM debian:bookworm

# allow the system to use two package managers (apt and pip), as we do it intentionally (needed since Debain Bookworm - see PEP 668
ENV PIP_BREAK_SYSTEM_PACKAGES=1

# Set local timezone
ENV TZ=Europe/Vienna
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

LABEL maintainer="wolfgang.hotwagner@ait.ac.at"

# Install necessary debian packages
ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends apt-utils
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-tz \
    python3-scipy \
    python3-pkg-resources \
    python3-setuptools \
    python3-dateutil \
    python3-six \
    python3-kafka \
    python3-cerberus \
    python3-yaml \
    python3-pylibacl \
    python3-urllib3 \
    python3-statsmodels \
    python3-pandas \
    libacl1-dev \
    postfix \
    procps \
    mailutils \
    sudo \
    curl \
    vim \
    postfix \
    openjdk-17-jre \
    locales \
    locales-all \
    rsyslog \
    git \
    mypy \
    wget

RUN sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen && \
    sed -i -e 's/# de_AT ISO-8859-1/de_AT ISO-8859-1/' /etc/locale.gen && \
    dpkg-reconfigure --frontend=noninteractive locales && \
    update-locale LANG=en_US.UTF-8

ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8


# RUN pip3 install coverage

# Copy logdata-anomaly-miner-sources
ADD source/root/usr/lib/logdata-anomaly-miner /usr/lib/logdata-anomaly-miner

# copy these files instead as symlinks would need absolute paths.
ADD source/root/etc/aminer/conf-available/ait-lds/* /etc/aminer/conf-enabled/
ADD source/root/etc/aminer/conf-available/generic/* /etc/aminer/conf-enabled/
ADD source/root/etc/aminer/conf-available/ait-lds /etc/aminer/conf-available/ait-lds
ADD source/root/etc/aminer/conf-available/generic /etc/aminer/conf-available/generic

# Entrypoint-wrapper
ADD scripts/aminerwrapper.sh /aminerwrapper.sh


# Prepare the system and link all python-modules
RUN ln -s /usr/lib/logdata-anomaly-miner/aminerremotecontrol.py /usr/bin/aminerremotecontrol \
	&& ln -s /usr/lib/logdata-anomaly-miner/aminer.py /usr/bin/aminer \
	&& chmod 0755 /usr/lib/logdata-anomaly-miner/aminer.py  \
	&& chmod 0755 /usr/lib/logdata-anomaly-miner/aminerremotecontrol.py \
	&& ln -s /usr/lib/python3/dist-packages/kafka /etc/aminer/conf-enabled/kafka \
	&& ln -s /usr/lib/python3/dist-packages/cerberus /etc/aminer/conf-enabled/cerberus \
	&& ln -s /usr/lib/python3/dist-packages/scipy /etc/aminer/conf-enabled/scipy \
	&& ln -s /usr/lib/python3/dist-packages/numpy /etc/aminer/conf-enabled/numpy \
	&& ln -s /usr/lib/python3/dist-packages/pkg_resources /etc/aminer/conf-enabled/pkg_resources \
	&& ln -s /usr/lib/python3/dist-packages/yaml /etc/aminer/conf-enabled/yaml \
	&& ln -s /usr/lib/python3/dist-packages/pytz /etc/aminer/conf-enabled/pytz \
	&& ln -s /usr/lib/python3/dist-packages/dateutil /etc/aminer/conf-enabled/dateutil \
	&& ln -s /usr/lib/python3/dist-packages/six.py /etc/aminer/conf-enabled/six.py \
	&& ln -s /usr/lib/python3/dist-packages/urllib3 /etc/aminer/conf-enabled/urllib3 \
	&& ln -s /usr/lib/python3/dist-packages/statsmodels /etc/aminer/conf-enabled/statsmodels \
	&& ln -s /usr/lib/python3/dist-packages/packaging /etc/aminer/conf-enabled/packaging \
	&& ln -s /usr/lib/python3/dist-packages/pandas /etc/aminer/conf-enabled/pandas \
	&& ln -s /usr/lib/python3/dist-packages/patsy /etc/aminer/conf-enabled/patsy \
	&& useradd -ms /usr/sbin/nologin aminer && mkdir -p /var/lib/aminer/log && chmod 0755 /aminerwrapper.sh \
    && chown aminer.aminer -R /var/lib/aminer && chmod 0755 /etc/aminer

RUN PACK=$(find /usr/lib/python3/dist-packages -name posix1e.cpython\*.so) && FILE=$(echo $PACK | awk -F '/' '{print $NF}') ln -s $PACK /usr/lib/logdata-anomaly-miner/$FILE

# Add config
ADD source/root/etc/aminer /etc/aminer

# Copy the testsuite
ADD aecid-testsuite /home/aminer/aecid-testsuite

RUN chown aminer.aminer -R /home/aminer \
    && ln -s /usr/lib/logdata-anomaly-miner/aminer /home/aminer/aecid-testsuite/aminer \
    && ln -s /etc/aminer/template_config.py /home/aminer/aecid-testsuite/demo/aminer/template_config.py \
    && ln -s /etc/aminer/template_config.yml /home/aminer/aecid-testsuite/demo/aminer/template_config.yml \
    && chmod +x /home/aminer/aecid-testsuite/*.sh \
    && echo "aminer ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/aminer

ADD scripts/testingwrapper.sh /testingwrapper.sh
ADD source /home/aminer/source
ADD docs /home/aminer/docs

RUN pip3 install orjson
RUN PACK=$(find /usr/local/lib/ -name orjson.cpython\*.so) && FILE=$(echo $PACK | awk -F '/' '{print $NF}') ln -s $PACK /usr/lib/logdata-anomaly-miner/$FILE

USER aminer
WORKDIR /home/aminer/aecid-testsuite

# The following volumes can be mounted
VOLUME ["/etc/aminer","/var/lib/aminer","/logs"]

ENTRYPOINT ["/testingwrapper.sh", "start"]
