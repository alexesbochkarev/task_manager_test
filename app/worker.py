import asyncio
import json
import uuid
from datetime import datetime, timezone

from aio_pika import IncomingMessage, connect_robust
from aiormq.exceptions import AMQPConnectionError
from sqlalchemy import select

from app.config import settings
from app.db.session import AsyncSessionLocal
from app.models.task import Task, TaskStatus


async def process_task(message: IncomingMessage) -> None:
    async with message.process():
        payload = json.loads(message.body.decode())
        task_id = uuid.UUID(payload["task_id"])

        async with AsyncSessionLocal() as session:
            task = await session.get(Task, task_id)
            if task is None or task.status == TaskStatus.CANCELLED:
                return

            # Фиксируем старт обработки до выполнения самой фоновой работы.
            task.status = TaskStatus.IN_PROGRESS
            task.started_at = datetime.now(timezone.utc)
            await session.commit()

            try:
                # Имитация фоновой обработки задачи.
                await asyncio.sleep(2)

                task = await session.scalar(select(Task).where(Task.id == task_id))
                if task is None or task.status == TaskStatus.CANCELLED:
                    return

                # Сохраняем итог обработки в самой задаче, чтобы API мог его отдать клиенту.
                task.status = TaskStatus.COMPLETED
                task.completed_at = datetime.now(timezone.utc)
                task.result = "Task processed successfully"
                await session.commit()
            except Exception as exc:
                task = await session.scalar(select(Task).where(Task.id == task_id))
                if task is None:
                    return

                task.status = TaskStatus.FAILED
                task.completed_at = datetime.now(timezone.utc)
                task.error_message = str(exc)
                await session.commit()
                raise


async def main() -> None:
    connection = None

    while connection is None:
        try:
            connection = await connect_robust(settings.rabbitmq_url)
        except AMQPConnectionError:
            await asyncio.sleep(3)

    async with connection:
        channel = await connection.channel()
        await channel.set_qos(prefetch_count=10)
        queue = await channel.declare_queue(settings.task_queue_name, durable=True)
        await queue.consume(process_task)
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
