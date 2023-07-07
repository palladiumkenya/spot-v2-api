from aio_pika import connect, Message, ExchangeType
from datetime import datetime
import json
from app.config.config import settings
from app.database import Dockets, Manifests, client
from app import schemas
from app.logger import logger


## TODO: ASK FOR MANIFEST_ID IF POSSIBLE
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
	try:
		pipeline = [
			{
				"$match": { "extracts.name": body_data["ExtractName"] }
			},
			{
				"$project": {
				"_id": 1,
				"extractId": {
					"$filter": {
						"input": "$extracts",
						"cond": { "$eq": ["$$this.name", body_data["ExtractName"]] }
					}
				}
				}
			},
			{
				"$project": {
					"_id": 1,
					"extractId": { "$arrayElemAt": ["$extractId.id", 0] }
				}
			}
		]
		docket_info = Dockets.aggregate(pipeline).next()
		# Start a MongoDB session for transactions
		with client.start_session() as session:
			# Start a transaction
			session.start_transaction()
			try:
				# Perform rollback on failure flag
				rollback = False

				# Update where document matches
				Manifests.update_one(
					{"mfl_code": body_data["SiteCode"], "is_current": True, "extract_id": docket_info["extractId"] },
					{"$inc": {"received": body_data["PatientPks"]}, "$set": {"updated_at": datetime.now(), "receivedDate": datetime.now()}}, 
					upsert=True
				)

				# Commit the transaction
				session.commit_transaction()

			except Exception as e:
				# Rollback the transaction if any exception occurs
				session.abort_transaction()
				rollback = True
				logger.error(e, exc_info=True)

			finally:
				# End the session
				session.end_session()

		# Check if rollback occurred
		if rollback:
			logger.error(f"---Inserting EXTRACT: {body_data['ExtractName']} SiteCode: {body_data['SiteCode']} failed.---")
			await message.reject() # Reject and discard the message
			return
		else:
			print(f"+++Inserting EXTRACT: {body_data['ExtractName']} SiteCode: {body_data['SiteCode']} successful+++")
	except Exception as e:
		logger.error(e, exc_info=True)
		await message.reject() # Reject and discard the message

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
	queue = await channel.declare_queue("extracts.queue", durable=True)

	await queue.bind(exchange, routing_key="extracts.route")

	# Start consuming messages from the queue
	await queue.consume(process_message)