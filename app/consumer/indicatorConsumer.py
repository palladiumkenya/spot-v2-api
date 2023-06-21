from aio_pika import connect, Message, ExchangeType
from datetime import datetime
import json
from app.config.config import settings
from app.database import Indicators
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
	if body_data.get("stage") == "EMR" or body_data.get("stage") is None:
		# Parse the message using the Pydantic schema
		try:
			message_data = schemas.IndicatorsBaseSchema.parse_raw(body)
			# Add extra columns
			message_data.created_at = datetime.now().isoformat()
			message_data.is_current = True
		except Exception as e:
			print("Invalid message format:", e)
			await message.reject()  # Reject and discard the message
			return

		try:
			validated_data = schemas.IndicatorsBaseSchema(
				**message_data.dict())
		except Exception as e:
			print("Invalid message data:", e)
			await message.reject()  # Reject and discard the message
			return

		# Update existing records with the same name and mfl_code to isCurrent=False
		filter_query = {
			"name": validated_data.name,
			"mfl_code": validated_data.mfl_code,
		}
		update_query = {
			"$set": {"is_current": False}
		}
		Indicators.update_many(filter_query, update_query)

		# Save the new record to MongoDB
		result = Indicators.insert_one(validated_data.dict())
	elif body_data.get("stage") == 'DWH':
		filter_query = {
			"name": body_data.get("name"),
			"mfl_code": body_data.get("mfl_code"),
			"is_current": True,
		}
		update_query = {
			"$set": {
				"dwh_value": body_data.get("dwh_value"),
				"dwh_indicator_date": body_data.get("dwh_indicator_date")
			}
		}
		Indicators.update_one(filter_query, update_query)
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
	queue = await channel.declare_queue("indicator.queue")
	# Set prefetch_count to the desired value

	await queue.bind(exchange, routing_key="indicator.route")

	# Start consuming messages from the queue
	await queue.consume(process_message)
