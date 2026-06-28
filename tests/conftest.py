import uuid
from collections.abc import AsyncGenerator
from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient

from app.db.session import get_async_session
from app.main import app
from app.models.task import Task, TaskStatus


class FakeScalarResult:
    def __init__(self, items):
        self._items = items

    def __iter__(self):
        return iter(self._items)


class FakeSession:
    def __init__(self) -> None:
        self.tasks: dict[uuid.UUID, Task] = {}

    def _touch(self, task: Task) -> None:
        task.updated_at = datetime.now(timezone.utc)

    def add(self, task: Task) -> None:
        now = datetime.now(timezone.utc)
        task.id = uuid.uuid4()
        task.status = TaskStatus.NEW
        task.created_at = now
        task.updated_at = now
        self.tasks[task.id] = task

    async def commit(self) -> None:
        for task in self.tasks.values():
            self._touch(task)

    async def refresh(self, task: Task) -> None:
        if task.id is not None and task.id in self.tasks:
            self._touch(task)

    async def get(self, model, task_id: uuid.UUID) -> Task | None:
        return self.tasks.get(task_id)

    async def scalar(self, query):
        query_str = str(query)
        if "count" in query_str.lower():
            if "WHERE" in query_str:
                status_value = query.compile().params.get("status_1")
                return sum(1 for task in self.tasks.values() if task.status == status_value)
            return len(self.tasks)

        task_id = query.compile().params.get("id_1")
        if task_id is None:
            return None
        return self.tasks.get(task_id)

    async def scalars(self, query) -> FakeScalarResult:
        tasks = list(self.tasks.values())
        query_str = str(query)
        if "WHERE" in query_str:
            status_value = query.compile().params.get("status_1")
            tasks = [task for task in tasks if task.status == status_value]
        tasks.sort(key=lambda task: task.created_at, reverse=True)
        return FakeScalarResult(tasks)


@pytest.fixture
def fake_session() -> FakeSession:
    return FakeSession()


@pytest.fixture
def client(fake_session: FakeSession) -> TestClient:
    async def override_session() -> AsyncGenerator[FakeSession, None]:
        yield fake_session

    app.dependency_overrides[get_async_session] = override_session

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
