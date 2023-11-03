from aio_pika import connect, Message, ExchangeType
from datetime import datetime
import json
from bson import ObjectId
from app.config.config import settings
from app.database import Manifests, Dockets, FacilityMetrics, Log, client
from app import schemas

## TODO:: FIND A WAY TO SAVE MISSING AND FIND A WAY TO SAVE DIFFERENTIAL
async def process_message(message: Message):
	# Process the received message
	body = message.body.decode()
	print("Received message:", body)
	facility_metrics = []

	log_id = ObjectId()
	Log.update_one(
			{"body": body},
			{"$set" : {"id": log_id, "body": body, "processed": False, "created_at": datetime.now(),  "queue": "manifest.queue"}, "$inc": { "retry" : 1 }},
			upsert=True
		)
	# Parse the message body as JSON
	try:
		body_data = json.loads(body)
	except json.JSONDecodeError as e:
		print("Invalid JSON format:", e)
		await message.reject()  # Reject and discard the message
		return
	if "manifest" in body_data:
		body_data = body_data["manifest"]
		try:
			manifest_data = {
				"manifest_id": body_data["Id"],
				"mfl_code": body_data["FacilityCode"],
				"upload_mode": body_data["UploadMode"],
				"emr_setup": body_data["EmrSetup"],
				"is_current": True,
				"log_id": log_id
			}
			stats_data = []
			facility_metrics.extend(
				(
					{"metric": "EMR Type", "value": body_data["EmrName"]},
					{"metric": "EMR Version", "value": body_data["EmrVersion"]},
					{"metric": "DWAPI Version", "value": body_data["DwapiVersion"]}
				)
			)
			if "Cargo" in body_data:
				metric = body_data["Cargo"]
				metric = json.loads(metric)

				for cargo in metric:
					if cargo["stats"] != None:
						docket = await get_docket(cargo)
						stats_data.append(
							{
								"expected": cargo["stats"],
								"docket_id": docket["_id"],
								"extract_id": docket["extractId"],
								"log_date": body_data["LogDate"],
								"session": body_data["Session"],
							}
						)

			for metric in body_data["Metrics"]:
				if metric["Type"] != 0 and metric["Name"] == "AppMetrics":
					value = metric["Value"]
					value = json.loads(value)
					log_value = json.loads(value["LogValue"])
					value["LogValue"] = log_value
					if log_value["Name"] == "CTSendStart":
						manifest_data["start"] = log_value["Start"]
					elif log_value["Name"] == "CTSendEnd":
						manifest_data["end"] = log_value["End"]

			for stat in stats_data:
				manifest_data |= stat
				try:
					# Add extra columns
					manifest_data["created_at"] = datetime.now()
					manifest_data["updated_at"] = datetime.now()

					validated_data = schemas.ManifestsSchema(**manifest_data)

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

						except Exception:
							# Rollback the transaction if any exception occurs
							session.abort_transaction()
							rollback = True

						finally:
							# End the session
							session.end_session()

					# Check if rollback occurred
					if rollback:
						print(f"---INSERTING MANIFEST Extract {manifest_data['extract_id']} SiteCode: {manifest_data['mfl_code']} FAILED. Rollback performed.---")
					else:
						print(f"+++INSERTING MANIFEST Extract {manifest_data['extract_id']} SiteCode: {manifest_data['mfl_code']} SUCCESSFUL.+++")

				except Exception as e:
					print("Invalid message format:", e)
					await message.reject()  # Reject and discard the message
					return

		except KeyError as e:
			print("Invalid JSON format:", e)
			await message.reject()  # Reject and discard the message
			return
		
		#save facility metrics
		if len(facility_metrics) > 0:
			save_facility_metrics(facility_metrics, manifest_data["mfl_code"])

	else:
		try:
			await handle_manifests(body_data, message, log_id)
		except:
			await message.reject()
	Log.update_one({"id": log_id}, {"$set": {"processed_at": datetime.now(), "processed": True}})
	# Acknowledge the message
	await message.ack()

async def consume_messages():
	# Connect to RabbitMQ
	connection = await connect(settings.RABBIT_URL)

	# Create a channel
	channel = await connection.channel()

	# Set prefetch_count to the desired value
	await channel.set_qos(prefetch_count=50)

	# Declare the exchange
	exchange = await channel.declare_exchange("spot.exchange", ExchangeType.DIRECT)

	# Declare the queue and bind it to the exchange
	queue = await channel.declare_queue("manifest.queue", durable=True)

	await queue.bind(exchange, routing_key="manifest.route")

	# Start consuming messages from the queue
	await queue.consume(process_message)

def save_facility_metrics(facility_metrics, mfl_code):
	"""
    Save facility metrics to the database.

    Args:
        facility_metrics (list of dict): List of facility metrics, each represented as a dictionary.
        mfl_code (str): MFL code associated with the facility.

    Returns:
        None
    """
	#Remove any duplicates from facility_metrics
	unique_facility_metrics = [dict(t) for t in {tuple(d.items()) for d in facility_metrics}]
	#Extract metric names found
	metric_names = [metric["metric"] for metric in unique_facility_metrics]
	# Add missing columns 
	metrics = [{**d, "mfl_code": mfl_code} for d in unique_facility_metrics]
	metrics = [{**d, "created_at": datetime.now()} for d in metrics]
	metrics = [{**d, "is_current": True} for d in metrics]
	#Update current facility metrics where the metricname and mflcode match 
	FacilityMetrics.update_many({"mfl_code": mfl_code, "metric": {"$in": metric_names}}, {"$set": {"is_current": False}}) 
	#Insert the new facility metrics
	FacilityMetrics.insert_many(metrics)

## TODO: Maybe handle this when they arent available in manifest
def handle_metrics(metric):
	cargo = json.loads(metric["Cargo"])
	return

async def handle_manifests(manifest, message, log_id):
	"""
    Handle manifest data and update the database with the provided manifest information for MNCH, HTS and PREP Dockets.
    
    Parameters:
    manifest (dict): A dictionary containing manifest data to be processed.

    Returns:
    None

    Raises:
    - KeyError: If the provided manifest dictionary is missing required keys.
    - ValueError: If there is an issue with the JSON format within the manifest data.
    
    Notes:
    - This function assumes the presence of specific keys in the manifest dictionary, and it may raise KeyError if any of these keys are missing.
    - The manifest dictionary should contain information about the manifest, including manifest ID, site code, upload mode, EMR setup, metrics, and other relevant data.
    - The function processes the metrics within the manifest and extracts specific information for database insertion.
    - It performs database transactions to update and insert data in the database.
    - Rollback is performed if any exception occurs during database operations.
    - Facility metrics and statistics data are processed and saved separately in the database.
    - The function uses the `save_facility_metrics` function to save facility metrics.
    
    """
	try:
		manifest_data = {
			"manifest_id": manifest["ManifestId"],
			"mfl_code": manifest["SiteCode"],
			"upload_mode": manifest["UploadMode"],
			"emr_setup": manifest["EmrSetup"],
			"is_current": True,
			"log_id": log_id
			# "status": body_data["Status"],
		}
		facility_metrics = []
		stats_data = []
		for metric in manifest["Metrics"]:
			if metric["Type"] == 0:
				continue
			value = metric["Items"]
			print(value)
			value = json.loads(value)
			if metric["Type"] == 1:
				facility_metrics.extend(
					(
						{"metric": "EMR Version", "value": value["EmrVersion"]},
						{"metric": "EMR Type", "value": value["EmrName"]},
					)
				)
			elif metric["Type"] != 0:
				log_value = json.loads(value["LogValue"])
				value["LogValue"] = log_value
				lookup = {
					"HTS": {
						"name": "HivTestingService",
						"start": "HTSSendStart",
						"end": "HTSSendEnd"
					},
					"MNCH": {
						"name": "MNCH",
						"start": "MNCHSendStart",
						"end": "MNCHSendEnd"
					},
					"PREP": {
						"name": "PREP",
						"start": "PREPSendStart",
						"end": "PREPSendEnd"
					}
				}
				current_manifest = lookup[manifest["Docket"]]
				if log_value["Name"] == current_manifest["start"]:
					manifest_data["start"] = log_value["Start"]
					if "Session" in log_value:
						manifest_data["session"] = log_value["Session"]
					elif "Session" in manifest:
						manifest_data["session"] = manifest["Session"]
					else:
						manifest_data["session"] = "missing"
				elif log_value["Name"] == current_manifest["start"]:
					manifest_data["end"] = log_value["End"]
				elif "ExtractCargos" in log_value and isinstance(log_value["ExtractCargos"], list) and value["Name"] == current_manifest["name"]:
					facility_metrics.append({
						"metric": "DWAPI Version",
						"value": log_value["Version"]
					})
					for cargo in log_value["ExtractCargos"]:
						docket = await get_docket(cargo)
						# print(docket)
						stats_data.append(
							{
								"expected": cargo["Stats"],
								"docket_id": docket["_id"],
								"extract_id": docket["extractId"],
								"log_date": value["LogDate"],
							}
						)

		for stat in stats_data:
			manifest_data |= stat
			try:
				# Add extra columns
				manifest_data["created_at"] = datetime.now()
				manifest_data["updated_at"] = datetime.now()

				validated_data = schemas.ManifestsSchema(**manifest_data)

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

					except Exception:
						# Rollback the transaction if any exception occurs
						session.abort_transaction()
						rollback = True

					finally:
						# End the session
						session.end_session()

				# Check if rollback occurred
				if rollback:
					print(f"---INSERTING MANIFEST Extract {manifest_data['extract_id']} SiteCode: {manifest_data['mfl_code']} FAILED. Rollback performed.---")
				else:
					print(f"+++INSERTING MANIFEST Extract {manifest_data['extract_id']} SiteCode: {manifest_data['mfl_code']} SUCCESSFUL.+++")

			except Exception as e:
				print("Invalid message format:", e)
				return
	except KeyError as e:
		print("Invalid 2 JSON format:", e)
		await message.ack()
		return
	#save facility metrics
	if len(facility_metrics) > 0:
		save_facility_metrics(facility_metrics, manifest_data["mfl_code"])
	return

async def get_docket(cargo):
	"""
    Get or create a docket & extract associated with the given cargo in the manifest.

    Args:
        cargo (dict): Cargo information containing the Extract(Cargo) name and docket ID.

    Returns:
        dict: Dictionary containing "extractId" and "_id" of the docket.
    """
	cargo = {key.lower(): value for key, value in cargo.items()}
	pipeline = [
		{
			"$match": { "extracts.name": cargo["name"] }
		},
		{
			"$project": {
			"_id": 1,
			"extractId": {
				"$filter": {
					"input": "$extracts",
					"cond": { "$eq": ["$$this.name", cargo["name"]] }
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
	docket = Dockets.aggregate(pipeline)
	try:
		docket = next(docket)
		return docket
	except StopIteration:
		# Handle the case when there are no results
		print("No results found.")
		obj_id = str(ObjectId())
		extract = {
			"id": obj_id, 
			"name": cargo["name"],
			"display": cargo["name"], 
			"isPatient": False,
			"rank": 30
		}

		Dockets.update_one(
			{ "name": cargo["DocketId"] },
			{ "$push": {"extracts": extract} }
		)
		docket_info = Dockets.aggregate([
			{
				"$match": { "name": cargo["DocketId"] }
			},
			{
				"$project": {"_id": 1}
			}
		])

		return {
			"extractId": obj_id,
			"_id": next(docket_info)["_id"]
		}
