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
	if body_data.get("IndicatorsExtracts")[0]["Stage"] == "EMR" or body_data.get("IndicatorsExtracts")[0]["Stage"] is None:
		# Parse the message using the Pydantic schema
		body_data = body_data["IndicatorsExtracts"]
		for data in body_data:
			indicator_data = {
				"mfl_code": data["FacilityCode"],
				"facility_manifest_id": data["FacilityManifestId"],
				"emr_indicator_date": data["IndicatorDate"],
				"emr_value": data["Value"],
				"name": data["Name"],
				"created_at": datetime.now(),
				"is_current": True
			}
			print(indicator_data)
			# try:
				
				# message_data = schemas.IndicatorsBaseSchema.parse_raw(indicator_data)
				# Add extra columns
				# indicator_data.created_at = datetime.now().isoformat()
				# indicator_data.is_current = True
			# except Exception as e:
			# 	print("Invalid message format:", e)
			# 	await message.reject()  # Reject and discard the message
			# 	return

			try:
				validated_data = schemas.IndicatorsBaseSchema(
					**indicator_data)
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
	
	# Set prefetch_count to the desired value increase when more proccessing power is available
	await channel.set_qos(prefetch_count=10)

	# Declare the exchange
	exchange = await channel.declare_exchange("spot.exchange", ExchangeType.DIRECT)

	# Declare the queue and bind it to the exchange
	queue = await channel.declare_queue("indicator.queue", durable=True)

	await queue.bind(exchange, routing_key="indicator.route")

	# Start consuming messages from the queue
	await queue.consume(process_message)
