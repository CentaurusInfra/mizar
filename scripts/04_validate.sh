#!/bin/bash

systemctl is-active --quiet transit

if [ $? -eq 0 ]
then
  logger "Successfully started transitd"
else
  logger "Failure starting transitd"
fi
