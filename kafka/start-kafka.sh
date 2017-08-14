#!/bin/sh
MACHINE_NAME=$1
eval $(docker-machine env ${MACHINE_NAME})
export ENV_CONFIG_FILE=`pwd`/config/dev.cfg
python load_data.py
