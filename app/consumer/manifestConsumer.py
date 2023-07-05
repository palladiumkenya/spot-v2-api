from aio_pika import connect, Message, ExchangeType
from datetime import datetime
import json
from app.config.config import settings
from app.database import Manifests, Dockets, client
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
	try:
		manifest_data = {
			"manifest_id": body_data["ManifestId"],
			"mfl_code": body_data["SiteCode"],
			"upload_mode": body_data["UploadMode"],
			"emr_setup": body_data["EmrSetup"],
			"is_current": True
			# "status": body_data["Status"],
		}
		stats_data = []
		for metric in body_data["Metrics"]:
			if metric["Type"] != 0 and metric["Name"] == "AppMetrics":
				value = metric["Value"]

				value = json.loads(value)
				log_value = json.loads(value["LogValue"])
				value["LogValue"] = log_value
				if log_value["Name"] == "CTSendStart":
					manifest_data["start"] = log_value["Start"]
					manifest_data["session"] = log_value["Session"]
				elif log_value["Name"] == "CTSendEnd":
					manifest_data["end"] = log_value["End"]
				elif "ExtractCargos" in log_value and isinstance(log_value["ExtractCargos"], list):
					for cargo in log_value["ExtractCargos"]:
						print(cargo)
						pipeline = [
							{
								"$match": { "extracts.name": cargo["Name"] }
							},
							{
								"$project": {
								"_id": 1,
								"extractId": {
									"$filter": {
										"input": "$extracts",
										"cond": { "$eq": ["$$this.name", cargo["Name"]] }
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
						docket = Dockets.aggregate(pipeline).next()
						stats_data.append(
							{
								"expected": cargo["Stats"],
								"docket_id": docket["_id"],
								"extract_id": docket["extractId"],
							}
						)
		print(stats_data)
		for stat in stats_data:
			manifest_data.update(stat)
			try:
				# Add extra columns
				manifest_data["created_at"] = datetime.now()

				# Find documents with matching mflcode and is_current is false
				matching_documents = Manifests.find({"mfl_code": manifest_data["mfl_code"], "is_current": True, "extract_id": manifest_data["extract_id"] })

				validated_data = schemas.ManifestsSchema(**manifest_data)
				print(validated_data)
				# Start a MongoDB session for transactions
				with client.start_session() as session:
					# Start a transaction
					session.start_transaction()

					try:
						# Perform rollback on failure flag
						rollback = False

						# Iterate over matching documents and update is_current to false
					
						Manifests.update_many(
							{"mfl_code": manifest_data["mfl_code"], "is_current": True, "extract_id": manifest_data["extract_id"] },
							{"$set": {"is_current": False}}
						)
						# Insert new document with is_current set to true
						Manifests.insert_one(validated_data.dict())


						# Commit the transaction
						session.commit_transaction()

					except:
						# Rollback the transaction if any exception occurs
						session.abort_transaction()
						rollback = True

					finally:
						# End the session
						session.end_session()

				# Check if rollback occurred
				if rollback:
					print("Insertion failed. Rollback performed.")
				else:
					print("Insertion successful. Updated matching documents.")

			except Exception as e:
				print("Invalid message format:", e)
				await message.reject()  # Reject and discard the message
				return
	
	except KeyError as e:
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
	queue = await channel.declare_queue("manifest.queue", durable=True)
	# Set prefetch_count to the desired value

	await queue.bind(exchange, routing_key="manifest.route")

	# Start consuming messages from the queue
	await queue.consume(process_message)