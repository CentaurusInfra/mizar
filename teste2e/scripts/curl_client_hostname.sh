IP=$1
TYPE=$2

if [ "$TYPE" == "scaled" ]
then
    curl http://$IP:8000 -Ss -m 5
else
    curl http://$IP:7000 -Ss -m 5
fi
