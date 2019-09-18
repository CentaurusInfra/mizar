#!/bin/bash

sudo docker ps -q | xargs -n 1 sudo docker inspect --format '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}} {{ .Name }}' | sed 's/ \// /'
