# logdata-anomaly-miner Dockerfile
#
# Build:
#    docker build -t aecid/logdata-anomaly-miner:latest -t aecid/logdata-anomaly-miner:$(grep '__version__ =' source/root/usr/lib/logdata-anomaly-miner/aminer.py | awk -F '"' '{print $2}') .
#
# See: https://github.com/ait-aecid/logdata-anomaly-miner/wiki/Deployment-with-Docker
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
        python3-urllib3 \
        libacl1-dev

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
	&& ln -s /usr/lib/python3/dist-packages/urllib3 /usr/lib/logdata-anomaly-miner/urllib3 \
	&& useradd -ms /usr/sbin/nologin aminer && mkdir -p /var/lib/aminer/logs && mkdir /etc/aminer \
        && chown aminer.aminer -R /var/lib/aminer \
        && chmod 0755 /aminerwrapper.sh

RUN PACK=$(find /usr/lib/python3/dist-packages -name posix1e.cpython\*.so) && FILE=$(echo $PACK | awk -F '/' '{print $NF}') ln -s $PACK /usr/lib/logdata-anomaly-miner/$FILE

USER aminer
WORKDIR /home/aminer

# The following volumes can be mounted
VOLUME ["/etc/aminer","/var/lib/aminer","/logs"]

ENTRYPOINT ["/aminerwrapper.sh"]

# Default command for the ENTRYPOINT(wrapper)
CMD ["aminer","--config","/etc/aminer/config.yml"]
