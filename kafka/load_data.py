import argparse
import json
import time
import logging
import schedule
import atexit
from apscheduler.schedulers.background import BackgroundScheduler
from googlefinance import getQuotes
from kafka import KafkaProducer
from flask import (
    Flask,
    request,
    jsonify
)
from flask_cors import CORS, cross_origin
from kafka.errors import (
    KafkaError,
    KafkaTimeoutError
)

logger_format = '%(asctime)-15s %(message)s'
logging.basicConfig(format=logger_format)
logger = logging.getLogger('load-data-log')
logger.setLevel(logging.DEBUG)

app = Flask(__name__)
app.config.from_envvar('ENV_CONFIG_FILE')
kafka_broker = app.config['CONFIG_KAFKA_ENDPOINT']
topic_name = app.config['CONFIG_KAFKA_TOPIC']
CORS(app)

producer = KafkaProducer(bootstrap_servers=kafka_broker)

schedule = BackgroundScheduler()
schedule.add_executor('threadpool')
schedule.start()

symbols = set()


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


def fetch_price(symbol):
    try:
        prices = json.dumps(getQuotes(symbol))
        logger.debug('get %s', prices)
        producer.send(topic=topic_name, value=prices, timestamp_ms=time.time())
    except KafkaTimeoutError as timeoutError:
        logger.warn(timeoutError)
    except Exception as e:
        logger.warn(e)


@app.route('/<symbol>', methods=['POST'])
def add_stock(symbol):
    if not symbol:
        return jsonify({
            'error': 'Stock symbol cannot be empty'
        }), 400
    if symbol in symbols:
        pass
    else:
        symbol = symbol.encode('utf-8')
        symbols.add(symbol)
        logger.info('Add stock retrieve job %s' % symbol)
        schedule.add_job(fetch_price, 'interval', [symbol], seconds=1, id=symbol)
    return jsonify(results=list(symbols)), 200


@app.route('/<symbol>', methods=['DELETE'])
def del_stock(symbol):
    if not symbol:
        return jsonify({
            'error': 'Stock symbol cannot be empty'
        }), 400
    if symbol not in symbols:
        pass
    else:
        symbols.remove(symbol)
        schedule.remove_job(symbol)
    return jsonify(results=list(symbols)), 200


if __name__ == '__main__':
    atexit.register(shutdown_hook, producer)
    app.run(host='0.0.0.0', port=app.config['CONFIG_APPLICATION_PORT'])

    # parser = argparse.ArgumentParser()
    # parser.add_argument('symbol')
    # parser.add_argument('topic')
    # parser.add_argument('kafka_broker')

    # args = parser.parse_args()
    # symbol = args.symbol
    # topic_name = args.topic
    # kafka_broker = args.kafka_broker
    #
    # schedule.every(1).second.do(fetch_price, producer, symbol)
    #
    # while True:
    #     schedule.run_pending()
    #     time.sleep(1)
