#!/bin/sh
MACHINE_NAME=$1
eval $(docker-machine env ${MACHINE_NAME})
python load_data.py stock-analyzer 192.168.99.100:9092 5000
