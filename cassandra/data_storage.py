import argparse
import atexit
import json
import logging
from cassandra.cluster import Cluster
from kafka import KafkaConsumer


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def shutdown_hook(kafka_consumer: KafkaConsumer, kafka_session: Cluster) -> None:
    """
    This function saves stock data to Cassandra.

    :param stock_data: The stock data to save.
    :param cassandra_session: The Cassandra session to use.
    :return: None
    """
    try:
        kafka_consumer.close()
        kafka_session.shutdown()
        logger.info('closed')
    except Exception as exception:
        logger.warning('close fails: %s', exception)


def persist_data(stock_data: str, cassandra_session: Cluster) -> None:
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
    sql = f'INSERT INTO {data_table} (stock_symbol, trade_time, trade_price) VALUES ({symbol}, {tradetime}, {price})'
    cassandra_session.execute(sql)
    logger.info('data written into cassandra %s', symbol)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('topic', type=str)
    parser.add_argument('kafka_broker', type=str)
    parser.add_argument('keyspace', type=str)
    parser.add_argument('data_table', type=str)
    parser.add_argument('cassandra_broker', type=str)

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
