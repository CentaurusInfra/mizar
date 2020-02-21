FROM python:3.7
RUN pip install kopf
RUN pip install kubernetes
RUN pip install pyyaml
RUN pip install netaddr
RUN pip install ipaddress
COPY mizar-k8s/operator/ /mizar/operator
COPY build/ /mizar/operator/build
RUN ln -snf /mizar/operator/build/bin /trn_bin
CMD kopf run --standalone /mizar/operator/app.py