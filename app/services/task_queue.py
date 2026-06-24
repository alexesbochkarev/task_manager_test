import json
import uuid

from aio_pika import DeliveryMode, Message, connect_robust

from app.config import settings


async def publish_task(task_id: uuid.UUID) -> None:
    connection = await connect_robust(settings.rabbitmq_url)
    async with connection:
        channel = await connection.channel()
        queue = await channel.declare_queue(settings.task_queue_name, durable=True)
        # Отправляем в очередь только идентификатор задачи, остальное воркер дочитает из БД.
        message = Message(
            body=json.dumps({"task_id": str(task_id)}).encode(),
            delivery_mode=DeliveryMode.PERSISTENT,
        )
        await channel.default_exchange.publish(message, routing_key=queue.name)
