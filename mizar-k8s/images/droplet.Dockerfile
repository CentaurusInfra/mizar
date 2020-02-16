FROM python:3.7
RUN pip install kopf
RUN pip install kubernetes
RUN pip install pyyaml
COPY droplet/ /mizar/droplet/
CMD python3 /mizar/droplet/app.py