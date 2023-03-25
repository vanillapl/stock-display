"""
read from kafka, process, write back to new kafka topic
"""
import sys
import time
import json
import logging
import atexit
from pyspark import SparkContext
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils
from kafka import KafkaProducer
from kafka.errors import (KafkaError, KafkaTimeoutError)

logger_format = '%(asctime)-15s %(message)s'
logging.basicConfig(format=logger_format)
logger = logging.getLogger('stream-process-log')
logger.setLevel(logging.DEBUG)

topic = ""
new_topic = ""
kafka_broker = ""
kafka_producer = None


def shutdown_hook(producer):
    try:
        producer.flush(10)
    except KafkaError as error:
        logger.warn('finish flushing')
    finally:
        try:
            producer.close(10)
            logger.info('closed')
        except Exception as e:
            logger.warn('close fails')


def process(stream):
    def send_to_kafka(rdd):
        results = rdd.collect()
        for r in results:
            data = json.dumps({
                'symbol': r[0],
                'timestamp': time.time(),
                'average': round(r[1], 3)
            })
            try:
                # logger.info('Sending average price %s to kafka' % data)
                kafka_producer.send(new_topic, value=data)
            except KafkaError as error:
                logger.warn(
                    'Failed to send data to kafka, caused by: %s', error.message)

    def pair(data):
        record = json.loads(data[1].decode('utf-8'))[0]
        return record.get('StockSymbol'), (float(record.get('LastTradePrice')), 1)

    stream.map(pair).reduceByKey(lambda a, b: (a[0] + b[0], a[1] + b[1]))\
        .map(lambda (k, v): (k, v[0]/v[1])).foreachRDD(send_to_kafka)


if __name__ == '__main__':

    if len(sys.argv) != 4:
        print('Usage: need 4 arguments')
        exit(1)
    topic, new_topic, kafka_broker = sys.argv[1:]

    sc = SparkContext("local[2]", "StockAvgPrice")
    sc.setLogLevel('ERROR')

    ssc = StreamingContext(sc, 5)

    # - create data stream
    directKafkaStream = KafkaUtils.createDirectStream(
        ssc, [topic], {'metadata.broker.list': kafka_broker})
    process(directKafkaStream)

    kafka_producer = KafkaProducer(bootstrap_servers=kafka_broker)

    atexit.register(shutdown_hook, kafka_producer)

    ssc.start()
    ssc.awaitTermination()
