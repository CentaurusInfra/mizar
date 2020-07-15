FROM python:3.7
RUN apt-get update -y
RUN apt-get install net-tools
RUN pip3 install PyYAML
RUN pip3 install kopf
RUN pip3 install netaddr
RUN pip3 install ipaddress
RUN pip3 install pyroute2
RUN pip3 install rpyc
RUN pip3 install kubernetes==11.0.0
RUN pip3 install luigi==2.8.12
RUN pip3 install grpcio
RUN pip3 install protobuf
RUN pip3 install fs
RUN mkdir -p /var/run/luigi
RUN mkdir -p /var/log/luigi
RUN mkdir -p /var/lib/luigi
RUN mkdir -p /etc/luigi
COPY etc/luigi.cfg /etc/luigi/luigi.cfg
