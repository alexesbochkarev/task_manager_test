import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.task import TaskPriority, TaskStatus


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    priority: TaskPriority = TaskPriority.MEDIUM


class TaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    description: str | None
    priority: TaskPriority
    status: TaskStatus
    created_at: datetime
    updated_at: datetime
    started_at: datetime | None
    completed_at: datetime | None
    result: str | None
    error_message: str | None


class TaskStatusResponse(BaseModel):
    id: uuid.UUID
    status: TaskStatus


class TaskListResponse(BaseModel):
    total: int
    limit: int
    offset: int
    items: list[TaskResponse]
