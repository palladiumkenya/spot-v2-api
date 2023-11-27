from aio_pika import connect, Message, ExchangeType
from datetime import datetime
import json
from bson import ObjectId
from app.config.config import settings
from app.database import SpotError, Log

async def process_message(message: Message):
	# Process the received message
	body = message.body.decode()
	print("Received message:", body)

	log_id = ObjectId()
	Log.insert_one({"id": log_id, "body": body, "processed": False, "created_at": datetime.now(),  "queue": "error.queue"})
	# Parse the message body as JSON
	try:
		body_data = json.loads(body)
	except json.JSONDecodeError as e:
		print("Invalid JSON format:", e)
		await message.reject()  # Reject and discard the message
		return
	
	SpotError.insert_one(body_data)

	Log.update_one({"id": log_id}, {"$set": {"processed_at": datetime.now(), "processed": True}})
	# Acknowledge the message
	await message.ack()


async def consume_messages():

	# Connect to RabbitMQ
	connection = await connect(settings.RABBIT_URL)

	# Create a channel
	channel = await connection.channel()
	
	# Set prefetch_count to the desired value increase when more proccessing power is available
	await channel.set_qos(prefetch_count=10)

	# Declare the exchange
	exchange = await channel.declare_exchange("spot.exchange", ExchangeType.DIRECT)

	# Declare the queue and bind it to the exchange
	queue = await channel.declare_queue("error.queue", durable=True)
	
	await queue.bind(exchange, routing_key="error.route")

	# Start consuming messages from the queue
	await queue.consume(process_message)
