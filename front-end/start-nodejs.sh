#!/bin/sh
MACHINE_NAME=$1
eval $(docker-machine env ${MACHINE_NAME})
IP=$(docker-machine ip ${MACHINE_NAME})
node index.js --port=8080 --redis_host=${IP} --redis_port=6379 --subscribe_topic=average-stock-price
