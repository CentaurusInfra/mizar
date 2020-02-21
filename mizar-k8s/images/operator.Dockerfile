FROM python:3.7
RUN pip install kopf
RUN pip install kubernetes
RUN pip install pyyaml
RUN pip install netaddr
RUN pip install ipaddress
COPY mizar-k8s/operator/ /mizar/operator
CMD kopf run --standalone /mizar/operator/app.py