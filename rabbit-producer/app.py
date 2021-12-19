import pika
import os
from flask import Flask
import requests
import json
import logging

RABBITMQ_HOST=os.getenv('RABBITMQ_HOST')
RABBITMQ_USER=os.getenv('RABBITMQ_USER')
RABBITMQ_PASS=os.getenv('RABBITMQ_PASS')
RANDOM_ENDPOINT=os.getenv('RANDOM_ENDPOINT')

def get_random():
    r = requests.get(RANDOM_ENDPOINT)
    return r.json()

app = Flask(__name__)

@app.route("/")
def push_queue():
    random_text = json.dumps(get_random())
    rabbit_credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(RABBITMQ_HOST, 5672, '/', rabbit_credentials))
    channel = connection.channel()
    channel.queue_declare(queue='hello')
    channel.basic_publish(exchange='', routing_key='hello', body=random_text)
    app.logger.info("Pushed to RabbitMQ. -- " + random_text)
    connection.close()
    return random_text