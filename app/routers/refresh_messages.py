import json
from datetime import datetime, timedelta
from fastapi import APIRouter
from aio_pika import connect, Message, ExchangeType
import asyncio
from app.config.config import settings
from app.database import Log

router = APIRouter()

@router.get("/manifest/resend")
async def trigger_manifest_fix():
    ten_minutes_ago = datetime.now() - timedelta(minutes=100)
    
    pipeline = [
        {
            "$match": {
                "queue": "manifest.queue",
                "created_at": {"$gte": ten_minutes_ago},
                "retry": { "$gte": 1 }
            }
        },
        {
            "$lookup": {
                "from": "manifests",
                "localField": "id",
                "foreignField": "log_id",
                "as": "matchingDocs"
            }
        },
        {
            "$match": {
                "matchingDocs": { "$size": 0 }
            }
        }
    ]

    result = list(Log.aggregate(pipeline))
    
    if len(result) >0:
        await message_fix(result)
    
    return {"message": f"{len(result)} found"}

@router.get("/resend/failed")
async def trigger_resend_all():
    asyncio.create_task(resend_all_messages())
    return {"message": "Resend requests started"}

@router.get("/resend/all")
async def trigger_resend_all():
    asyncio.create_task(resend_all_messages())
    return {"message": "Resend requests started"}

@router.get("/resend/{queue}")
async def trigger_resend_queue(queue:str):
    if queue in {'manifest', 'extracts', 'indicator', 'handshake'}:
        asyncio.create_task(resend_messages(queue))
    return {"message": f"Resend {queue} requests started"}

async def resend_all_messages():
    messages = Log.find({})
    # Connect to RabbitMQ
    connection = await connect(settings.RABBIT_URL)

    # Create a channel
    channel = await connection.channel()

    # Declare the exchange
    exchange = await channel.declare_exchange("spot.exchange", ExchangeType.DIRECT)

    for m in messages:
        # Declare the queue and bind it to the exchange
        queue = await channel.declare_queue(m["queue"], durable=True)
        # Publish the data item message to the queue
        message = Message(
            body=m["body"].encode("utf-8"),  # Encode the JSON as bytes
            content_type="application/json",  # Set the content type to JSON
        )
        if m["queue"] in {'manifest.queue', 'extracts.queue', 'indicator.queue', 'handshake.queue'}:
            await exchange.publish(message, routing_key=f'{m["queue"].split(".", 1)[0]}.route')

    # Close the connection
    await connection.close()

async def resend_failed_messages():
    messages = Log.find({"processed": False})
    # Connect to RabbitMQ
    connection = await connect(settings.RABBIT_URL)

    # Create a channel
    channel = await connection.channel()

    # Declare the exchange
    exchange = await channel.declare_exchange("spot.exchange", ExchangeType.DIRECT)

    for m in messages:
        # Declare the queue and bind it to the exchange
        queue = await channel.declare_queue(m["queue"], durable=True)
        # Publish the data item message to the queue
        message = Message(
            body=m["body"].encode("utf-8"),  # Encode the JSON as bytes
            content_type="application/json",  # Set the content type to JSON
        )
        if m["queue"] in {'manifest.queue', 'extracts.queue', 'indicator.queue', 'handshake.queue'}:
            await exchange.publish(message, routing_key=f'{m["queue"].split(".", 1)[0]}.route')
            Log.update_one({"_id": m["_id"]},{"$in": {"tries": 1}})

    # Close the connection
    await connection.close()

async def resend_messages(item):
    messages = Log.find({"queue": f"{item}.queue", "processed": False})
    # Connect to RabbitMQ
    connection = await connect(settings.RABBIT_URL)

    # Create a channel
    channel = await connection.channel()

    # Declare the exchange
    exchange = await channel.declare_exchange("spot.exchange", ExchangeType.DIRECT)

    for m in messages:
        # Declare the queue and bind it to the exchange
        queue = await channel.declare_queue(m["queue"], durable=True)
        # Publish the data item message to the queue
        message = Message(
            body=m["body"].encode("utf-8"),  # Encode the JSON as bytes
            content_type="application/json",  # Set the content type to JSON
        )
        await exchange.publish(message, routing_key=f"{item}.route")

    # Close the connection
    await connection.close()

async def message_fix(messages):
    # Connect to RabbitMQ
    connection = await connect(settings.RABBIT_URL)

    # Create a channel
    channel = await connection.channel()

    # Declare the exchange
    exchange = await channel.declare_exchange("spot.exchange", ExchangeType.DIRECT)

    for m in messages:
        if "manifest" in m["body"] or "ManifestId" in m["body"]:
            Log.update_one({"_id": m["_id"]}, {"$inc": {"retry":1}})
            # Declare the queue and bind it to the exchange
            queue = await channel.declare_queue("manifest.queue", durable=True)
            # Publish the data item message to the queue
            message = Message(
                body=m["body"].encode("utf-8"),  # Encode the JSON as bytes
                content_type="application/json",  # Set the content type to JSON
            )
            await exchange.publish(message, routing_key="manifest.route")
    # Close the connection
    await connection.close()
    return messages
