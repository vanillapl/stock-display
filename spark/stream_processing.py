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
from kafka.errors import KafkaError, KafkaTimeoutError

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


def process(timeobj, rdd):
    num = rdd.count()
    if not num:
        return
    price_sum = rdd.map(lambda record: float(json.loads(record[1].decode('utf-8'))[0].get('LastTradePrice')))\
        .reduce(lambda x, y: x + y)
    price_avg = price_sum / num
    logger.info('Received %d records, avg price is %f' % (num, price_avg))

    data = json.dumps({
        'timestamp': time.time(),
        'average': price_avg
    })
    kafka_producer.send(new_topic, value=data)

if __name__ == '__main__':

    if len(sys.argv) != 4:
        print('Usage: need 4 arguments')
        exit(1)
    topic, new_topic, kafka_broker = sys.argv[1:]

    sc = SparkContext("local[2]", "StockAvgPrice")
    sc.setLogLevel('ERROR')

    ssc = StreamingContext(sc, 5)

    # - create data stream
    directKafkaStream = KafkaUtils.createDirectStream(ssc, [topic], {'metadata.broker.list': kafka_broker})
    directKafkaStream.foreachRDD(process)

    kafka_producer = KafkaProducer(bootstrap_servers=kafka_broker)

    atexit.register(shutdown_hook, kafka_producer)

    ssc.start()
    ssc.awaitTermination()
