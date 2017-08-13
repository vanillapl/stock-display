#!/bin/sh
export ENV_CONFIG_FILE=`pwd`/config/dev.cfg
python load_data.py
