# logdata-anomaly-miner Dockerfile
#
# Use build-script to create docker:
#    scripts/build_docker.sh
#
# Build manually:
#    docker build -t aecid/logdata-anomaly-miner:latest -t aecid/logdata-anomaly-miner:$(grep '__version__ =' source/root/usr/lib/logdata-anomaly-miner/metadata.py | awk -F '"' '{print $2}') .
#
# See: https://github.com/ait-aecid/logdata-anomaly-miner/wiki/Deployment-with-Docker
#

# Pull base image.
FROM debian:bullseye
ARG UNAME=aminer
ARG UID=1000
ARG GID=1000

# Set local timezone
ENV TZ=Europe/Vienna
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

LABEL maintainer="wolfgang.hotwagner@ait.ac.at"

# Install necessary debian packages
ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y \
    supervisor \
    python3 \
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
    python3-statsmodels \
    libacl1-dev

# Docs
RUN apt-get update && apt-get install -y \
    python3-sphinx \
    python3-sphinx-rtd-theme \
    python3-recommonmark \
    make

# For Docs
ADD docs /docs
ADD README.md /docs
ADD SECURITY.md /docs
ADD LICENSE /docs/LICENSE.md


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
	&& chmod 0755 /etc/aminer \
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
	&& ln -s /usr/lib/python3/dist-packages/statsmodels /usr/lib/logdata-anomaly-miner/statsmodels \
	&& ln -s /usr/lib/python3/dist-packages/packaging /usr/lib/logdata-anomaly-miner/packaging \
	&& groupadd -g $GID -o $UNAME && useradd -u $UID -g $GID -ms /usr/sbin/nologin $UNAME && mkdir -p /var/lib/aminer/logs \
    && chown $UID.$GID -R /var/lib/aminer \
    && chown $UID.$GID -R /docs \
    && chmod 0755 /aminerwrapper.sh

RUN PACK=$(find /usr/lib/python3/dist-packages -name posix1e.cpython\*.so) && FILE=$(echo $PACK | awk -F '/' '{print $NF}') ln -s $PACK /usr/lib/logdata-anomaly-miner/$FILE

RUN pip3 install orjson
RUN PACK=$(find /usr/local/lib/ -name orjson.cpython\*.so) && FILE=$(echo $PACK | awk -F '/' '{print $NF}') ln -s $PACK /usr/lib/logdata-anomaly-miner/$FILE


# Prepare Supervisord
COPY scripts/supervisord.conf /etc/supervisor/conf.d/supervisord.conf
RUN mkdir /var/lib/supervisor && chown $UID.$GID -R /var/lib/supervisor \
    && chown $UID.$GID -R /var/log/supervisor/

USER aminer
WORKDIR /home/aminer

# The following volumes can be mounted
VOLUME ["/etc/aminer","/var/lib/aminer","/logs"]

ENTRYPOINT ["/aminerwrapper.sh"]

# Default command for the ENTRYPOINT(wrapper)
CMD ["aminer","--config","/etc/aminer/config.yml"]
