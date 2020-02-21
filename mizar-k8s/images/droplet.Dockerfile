FROM python:3.7
RUN pip install kopf
RUN pip install kubernetes
RUN pip install pyyaml
RUN apt-get update && apt-get install -y --no-install-recommends apt-utils
RUN apt-get install -y sudo rpcbind rsyslog libelf-dev iproute2  net-tools iputils-ping ethtool curl
COPY mizar-k8s/droplet/ /var/mizar/droplet/
COPY build/ /var/mizar/droplet/build
CMD python3 /var/mizar/droplet/app.py