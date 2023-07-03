from aio_pika import connect, Message, ExchangeType
from datetime import datetime
import json
from app.config.config import settings
from app.database import Manifests
from app import schemas


async def process_message(message: Message):
	# Process the received message
	body = message.body.decode()
	print("Received message:", body)

	# Parse the message body as JSON
	try:
		body_data = json.loads(body)
	except json.JSONDecodeError as e:
		print("Invalid JSON format:", e)
		await message.reject()  # Reject and discard the message
		return

	# Validate the parsed message data against the schema
	
	# Acknowledge the message
	await message.ack()


async def consume_messages():

	# Connect to RabbitMQ
	connection = await connect(settings.RABBIT_URL)

	# Create a channel
	channel = await connection.channel()

	# Declare the exchange
	exchange = await channel.declare_exchange("spot.exchange", ExchangeType.DIRECT)

	# Declare the queue and bind it to the exchange
	queue = await channel.declare_queue("manifest.queue")
	# Set prefetch_count to the desired value

	await queue.bind(exchange, routing_key="manifest.route")

	# Start consuming messages from the queue
	await queue.consume(process_message)
