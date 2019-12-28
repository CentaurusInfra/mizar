#!/bin/bash

pgrep transitd

if [ $? -eq 0 ]
then
  logger "Successfully started transitd"
else
  logger "Failure starting transitd"
fi
