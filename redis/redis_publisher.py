"""
read from kafka, write to redis pub (like a message queue)
"""

from kafka import KafkaConsumer
import argparse
import atexit
import logging
import redis

topic_name = ""
kafka_broker = ""

logger_format = '%(asctime)-15s %(message)s'
logging.basicConfig(format=logger_format)
logger = logging.getLogger('load-data-log')
logger.setLevel(logging.DEBUG)


def shutdown_hook(consumer):
    try:
        consumer.close()
        logger.info('closed')
    except Exception as e:
        logger.warn('close fails')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('topic_name')
    parser.add_argument('kafka_broker')
    parser.add_argument('redis_channel')
    parser.add_argument('redis_host')
    parser.add_argument('redis_port')

    args = parser.parse_args()
    topic_name = args.topic_name
    kafka_broker = args.kafka_broker
    redis_channel = args.redis_channel
    redis_host = args.redis_host
    redis_port = args.redis_port

    kafka_consumer = KafkaConsumer(topic_name, bootstrap_servers=kafka_broker)

    redis_client = redis.StrictRedis(host=redis_host, port=redis_port)

    for msg in kafka_consumer:
        logger.info('Receive data: %s' % str(msg))
        redis_client.publish(redis_channel, msg.value)

    atexit.register(shutdown_hook, consumer)