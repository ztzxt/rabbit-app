import pika
import sys
import os
import logging
from datetime import datetime
from elasticsearch import Elasticsearch
from datetime import datetime
import json

RABBITMQ_HOST=os.getenv('RABBITMQ_HOST')
RABBITMQ_USER=os.getenv('RABBITMQ_USER')
RABBITMQ_PASS=os.getenv('RABBITMQ_PASS')
ELASTIC_HOST=os.getenv('ELASTIC_HOST')

es_index = 'rabbitmq-output'
def main():
    es = Elasticsearch(ELASTIC_HOST)
    logging.critical(es)
    if not es.indices.exists(index=es_index):
        es.indices.create(index=es_index)

    rabbit_credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(RABBITMQ_HOST, 5672, '/', rabbit_credentials))
    channel = connection.channel()

    channel.queue_declare(queue='hello')

    def callback(ch, method, properties, message):
        logging.info("Received from RabbitMQ -- " + message.decode('utf-8'))
        es_payload = json.loads(message)
        es_payload['timestamp'] = datetime.now()
        es.index(index=es_index, body=es_payload)
    channel.basic_consume(queue='hello', on_message_callback=callback, auto_ack=True)
    logging.info("Started receiving.")
    channel.start_consuming()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logging.error("Interrupted")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)