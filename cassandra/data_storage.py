"""
read from Kafka, write to Cassandra table
"""

import argparse
import json
import logging

import atexit
from cassandra.cluster import Cluster
from kafka import KafkaConsumer
from kafka.errors import KafkaError, KafkaTimeoutError

logger_format = '%(asctime)-15s %(message)s'
logging.basicConfig(format=logger_format)
logger = logging.getLogger('store-data-log')
logger.setLevel(logging.DEBUG)

topic_name = 'stock_analyzer'
kafka_broker = '127.0.0.1:9092'
keyspace = 'stock'
data_table = ''
cassandra_broker = '127.0.0.1:9042'


def shutdown_hook(consumer, session):
    try:
        consumer.close()
        session.shutdown()
        logger.info('closed')
    except Exception as e:
        logger.warn('close fails')


def persist_data(stock_data, cassandra_session):
    """
    
    :param stock_data: 
    :param cassandra_session: 
    :return: 
    """
    # logger.debug(stock_data)
    parse = json.loads(stock_data)[0]
    symbol = parse.get('StockSymbol')
    price = float(parse.get('LastTradePrice'))
    tradetime = parse.get('LastTradeDateTime')
    sql = "INSERT INTO %s (stock_symbol, trade_time, trade_price) VALUES ('%s', '%s', %f)" \
          % (data_table, symbol, tradetime, price)
    cassandra_session.execute(sql)
    logger.info('data written into cassandra %s' % (symbol))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('topic')
    parser.add_argument('kafka_broker')
    parser.add_argument('keyspace')
    parser.add_argument('data_table')
    parser.add_argument('cassandra_broker')

    # - parse arguments
    args = parser.parse_args()
    topic_name = args.topic
    kafka_broker = args.kafka_broker
    keyspace = args.keyspace
    data_table = args.data_table
    cassandra_broker = args.cassandra_broker
    # - kafka consumer
    consumer = KafkaConsumer(topic_name, bootstrap_servers=kafka_broker)
    # - cassandra session
    cassandra_cluster = Cluster(contact_points=cassandra_broker.split(','))
    session = cassandra_cluster.connect(keyspace)
    atexit.register(shutdown_hook, consumer, session)

    for msg in consumer:
        # - save data to cassandra
        persist_data(msg.value, session)
