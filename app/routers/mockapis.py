from fastapi import APIRouter
from aio_pika import connect, Message, ExchangeType
from datetime import datetime
import asyncio
import json
from app.config.config import settings


router = APIRouter()

@router.get("/send_mock_requests")
async def trigger_mock_requests():
    asyncio.create_task(send_mock_indicator())
    # asyncio.create_task(send_mock_requests())
    return {"message": "Mock requests sent"}

async def send_mock_requests():
    # Connect to RabbitMQ with the desired vhost
    connection = await connect(settings.RABBIT_URL)

    # Create a channel and a queue
    channel = await connection.channel()
    queue = await channel.declare_queue("test_queue")

    # Define the mock requests to send
    mock_requests = [
        {"id": 1, "message": "Request 1"},
        {"id": 2, "message": "Request 2"},
        # Add more mock requests as needed
    ]

    # Publish the mock requests to the queue
    for request in mock_requests:
        message_body = str(request).encode()
        message = Message(body=message_body)
        await channel.default_exchange.publish(message, routing_key=queue.name)

    # Close the connection
    await connection.close()

async def send_mock_indicator():
    # Connect to RabbitMQ
    connection = await connect(settings.RABBIT_URL)

    # Create a channel
    channel = await connection.channel()

    # Declare the exchange
    exchange = await channel.declare_exchange("spot.exchange", ExchangeType.DIRECT)

    # Declare the queue and bind it to the exchange
    queue = await channel.declare_queue("indicator.queue")

    # Define the mock data to send
    mock_data = [
        {
        "mfl_code": 14020,
        "facility_manifest_id": "456",
        "name": "TX_CURR",
        "emr_value": 890,
        "emr_indicator_date": datetime.now().isoformat(),
    },
    {
        "mfl_code": 12663,
        "facility_manifest_id": "012",
        "name": "TX_NEW",
        "emr_value": 20,
        "emr_indicator_date": datetime.now().isoformat(),
    },
    {
        "mfl_code": 12663,
        "facility_manifest_id": "012",
        "stage": "DWH",
        "name": "TX_NEW",
        "dwh_value": 22,
        "dwh_indicator_date": datetime.now().isoformat(),
    },
    ]

    for data in mock_data:
        data_item_json = json.dumps(data)

        # Publish the data item message to the queue
        message = Message(
            body=data_item_json.encode("utf-8"),
            content_type="application/json",
        )
        await exchange.publish(message, routing_key="indicator.route")

    # Close the connection
    await connection.close()
