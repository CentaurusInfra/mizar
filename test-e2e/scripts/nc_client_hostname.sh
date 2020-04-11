IP=$1
PROTOCOL=${2:-tcp}

if [ "$PROTOCOL" == "udp" ]
then
    echo test | nc $IP 9001 -w1
else
    echo test | nc -u $IP 5001 -w1
fi
