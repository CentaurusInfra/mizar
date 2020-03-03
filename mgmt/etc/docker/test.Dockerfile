FROM python:3.7
RUN apt-get update -y
RUN apt-get install iputils-ping
CMD while true; do echo "test"; sleep 2; done