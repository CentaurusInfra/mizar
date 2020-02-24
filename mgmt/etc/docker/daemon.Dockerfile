FROM python:3.7
RUN pip install kopf
RUN pip install kubernetes
RUN pip install pyyaml
RUN pip install rpyc
COPY mgmt/ /var/mizar/mgmt/
CMD python3 /var/mizar/mgmt/daemon.py