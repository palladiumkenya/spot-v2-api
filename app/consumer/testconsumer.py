
from aio_pika import connect, Message
from app.config.config import settings

async def process_message(message: Message):
    # Process the received message
    body = message.body.decode()
    print("Received message:", body)

    # Acknowledge the message
    await message.ack()


async def consume_messages():
    # Connect to RabbitMQ
    connection = await connect(settings.RABBIT_URL)

    # Create a channel and a queue
    channel = await connection.channel()
    queue = await channel.declare_queue("test_queue")

    # Start consuming messages
    await queue.consume(process_message)