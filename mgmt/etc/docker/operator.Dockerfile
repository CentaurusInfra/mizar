FROM python:3.7
RUN pip install kopf
RUN pip install kubernetes
RUN pip install pyyaml
RUN pip install netaddr
RUN pip install ipaddress
RUN pip install rpyc
RUN pip install luigi
COPY mgmt/ /var/mizar/mgmt/
COPY build/ /var/mizar/mgmt/build
RUN ln -snf /var/mizar/mgmt/build/bin /trn_bin
CMD kopf run --standalone /var/mizar/mgmt/operator.py