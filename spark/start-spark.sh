#!/bin/sh
MACHINE_NAME=$1
eval $(docker-machine env ${MACHINE_NAME})
IP=$(docker-machine ip ${MACHINE_NAME})
spark-submit --jars spark-streaming-kafka-0-8-assembly_2.11-2.2.0.jar stream_processing.py stock-analyzer average-stock-price ${IP}:9092
