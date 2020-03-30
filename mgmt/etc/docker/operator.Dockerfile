FROM python:3.7
RUN pip install kopf
RUN pip install kubernetes
RUN pip install pyyaml
RUN pip install netaddr
RUN pip install ipaddress
RUN pip install rpyc
RUN pip install luigi
RUN apt-get update -y
RUN apt-get install net-tools
COPY mgmt/ /var/mizar/mgmt/
COPY build/ /var/mizar/mgmt/build
RUN ln -snf /var/mizar/mgmt/build/bin /trn_bin
RUN mkdir -p /var/run/luigi
RUN mkdir -p /var/log/luigi
RUN mkdir -p /var/lib/luigi
RUN mkdir -p /etc/luigi
COPY mgmt/etc/luigi.cfg /etc/luigi/luigi.cfg
CMD kopf run --standalone /var/mizar/mgmt/operator.py