import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_async_session
from app.models.task import Task, TaskStatus
from app.schemas.task import TaskCreate, TaskListResponse, TaskResponse, TaskStatusResponse
from app.services.task_queue import publish_task


router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    payload: TaskCreate,
    session: AsyncSession = Depends(get_async_session),
) -> Task:
    task = Task(
        title=payload.title,
        description=payload.description,
        priority=payload.priority,
    )
    session.add(task)
    await session.commit()
    await session.refresh(task)

    try:
        await publish_task(task.id)
    except Exception as exc:
        task.status = TaskStatus.FAILED
        task.error_message = "Failed to publish task to queue"
        await session.commit()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Task queue is unavailable",
        ) from exc

    task.status = TaskStatus.PENDING
    task.error_message = None
    await session.commit()
    await session.refresh(task)
    return task


@router.get("", response_model=TaskListResponse)
async def list_tasks(
    status_filter: TaskStatus | None = Query(default=None, alias="status"),
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    session: AsyncSession = Depends(get_async_session),
) -> TaskListResponse:
    filters = []
    if status_filter is not None:
        filters.append(Task.status == status_filter)

    total_query = select(func.count()).select_from(Task)
    tasks_query = select(Task).order_by(Task.created_at.desc()).limit(limit).offset(offset)

    if filters:
        total_query = total_query.where(*filters)
        tasks_query = tasks_query.where(*filters)

    total = await session.scalar(total_query)
    tasks = await session.scalars(tasks_query)

    return TaskListResponse(
        total=total or 0,
        limit=limit,
        offset=offset,
        items=list(tasks),
    )


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: uuid.UUID,
    session: AsyncSession = Depends(get_async_session),
) -> Task:
    task = await session.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_task(
    task_id: uuid.UUID,
    session: AsyncSession = Depends(get_async_session),
) -> Response:
    task = await session.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    task.status = TaskStatus.CANCELLED
    await session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{task_id}/status", response_model=TaskStatusResponse)
async def get_task_status(
    task_id: uuid.UUID,
    session: AsyncSession = Depends(get_async_session),
) -> TaskStatusResponse:
    task = await session.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    return TaskStatusResponse(id=task.id, status=task.status)
