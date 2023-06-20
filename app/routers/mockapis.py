from fastapi import APIRouter
from aio_pika import connect, Message
import asyncio
from app.config.config import settings


router = APIRouter()

@router.get("/send_mock_requests")
async def trigger_mock_requests():
    asyncio.create_task(send_mock_requests())
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