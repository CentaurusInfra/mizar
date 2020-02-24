FROM kindest/node:v1.17.2
RUN apt-get update -y
RUN apt-get install -y apt-utils
RUN apt-get install -y sudo
RUN apt-get install -y vim
RUN apt-get install -y rpcbind
RUN apt-get install -y rsyslog
RUN apt-get install -y libelf-dev
RUN apt-get install -y iproute2
RUN apt-get install -y net-tools
RUN apt-get install -y iputils-ping
RUN apt-get install -y ethtool
RUN apt-get install -y curl
RUN apt-get install -y python3
RUN apt-get install -y python3-pip
RUN pip3 install kopf
RUN pip3 install kubernetes
RUN pip3 install pyyaml
RUN pip3 install netaddr
RUN pip3 install ipaddress
RUN pip3 install pyroute2
RUN pip3 install rpyc
RUN mkdir -p /var/mizar/
RUN mkdir -p /opt/cni/bin
RUN mkdir -p /etc/cni/net.d
RUN ln -snf /sys/fs/bpf /bpffs
RUN ln -snf /var/mizar/build/bin /trn_bin
RUN ln -snf /var/mizar/build/xdp /trn_xdp
RUN ln -snf /var/mizar/mgmt/etc/cni/10-mizarcni.conf /etc/cni/net.d/10-mizarcni.conf
RUN ln -snf /var/mizar/mgmt/cni.py /opt/cni/bin/mizarcni
RUN ln -snf /var/mizar/build/tests/mizarcni.config /etc/mizarcni.config

