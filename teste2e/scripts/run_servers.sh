#/bin/bash

SCRIPTS_DIR='/var/mizar/test/scripts'

python3 $SCRIPTS_DIR/httpd_hostname.py &
python3 $SCRIPTS_DIR/tcp_hostname.py &
python3 $SCRIPTS_DIR/udp_hostname.py &
while true; do echo "test"; sleep 2; done
