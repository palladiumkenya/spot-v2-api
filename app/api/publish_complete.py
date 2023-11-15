from fastapi import FastAPI, BackgroundTasks, Depends
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import aio_pika
from app.config.config import settings
from app.database import Profiles, Manifests

RABBITMQ_QUEUE = "completenotice.queue"
RABBITMQ_ROUTE = "completenotice.route"


async def send_to_rabbitmq(message: str):
	
	# Connect to RabbitMQ
	connection = await aio_pika.connect(settings.RABBIT_URL)

	# Create a channel
	channel = await connection.channel()

	# Declare the exchange
	exchange = await channel.declare_exchange("spot.exchange", aio_pika.ExchangeType.DIRECT)
	
	queue = await channel.declare_queue(RABBITMQ_QUEUE, durable=True)
	# Publish the data item message to the queue
	m = aio_pika.Message(
		body=message.encode("utf-8"),  # Encode the JSON as bytes
		content_type="application/json",  # Set the content type to JSON
	)
	await exchange.publish(m, routing_key=RABBITMQ_ROUTE)

	await connection.close()

