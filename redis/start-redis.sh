#!/bin/sh
MACHINE_NAME=$1
eval $(docker-machine env ${MACHINE_NAME})
IP=$(docker-machine ip ${MACHINE_NAME})
python redis_publisher.py average-stock-price 192.168.99.100:9092 average-stock-price 192.168.99.100 6379
