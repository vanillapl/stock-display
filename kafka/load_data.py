import argparse
import json
import time
import logging
import schedule
import atexit
from googlefinance import getQuotes
from kafka import KafkaProducer
from kafka.errors import KafkaError, KafkaTimeoutError

logger_format = '%(asctime)-15s %(message)s'
logging.basicConfig(format=logger_format)
logger = logging.getLogger('load-data-log')
logger.setLevel(logging.DEBUG)

topic_name = 'stock_analyzer'
kafka_broker = '127.0.0.1:9092'


def shutdown_hook(producer):
    try:
        producer.flush(10)
    except KafkaError as error:
        logger.warn('finish flushing')
    finally:
        try:
            producer.close()
            logger.info('closed')
        except Exception as e:
            logger.warn('close fails')


def fetch_price(producer, symbol):
    try:
        prices = json.dumps(getQuotes(symbol))
        logger.debug('get %s', prices)
        producer.send(topic=topic_name, value=prices, timestamp_ms=time.time())
    except KafkaTimeoutError as timeouterror:
        logger.warn(timeouterror)
    except Exception as e:
        logger.warn(e)



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('symbol')
    parser.add_argument('topic')
    parser.add_argument('kafka_broker')

    args = parser.parse_args()
    symbol = args.symbol
    topic_name = args.topic
    kafka_broker = args.kafka_broker

    producer = KafkaProducer(bootstrap_servers=kafka_broker)
    schedule.every(1).second.do(fetch_price, producer, symbol)

    atexit.register(shutdown_hook, producer)

    while True:
        schedule.run_pending()
        time.sleep(1)
