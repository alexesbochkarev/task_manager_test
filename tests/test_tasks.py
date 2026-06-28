from unittest.mock import AsyncMock, patch

from app.models.task import TaskStatus


def test_create_task_marks_task_pending_when_queue_is_available(client, fake_session) -> None:
    with patch("app.api.routes.tasks.publish_task", new=AsyncMock()) as publish_task_mock:
        response = client.post(
            "/api/v1/tasks",
            json={
                "title": "Test task",
                "description": "Run async processing",
                "priority": "HIGH",
            },
        )

    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "PENDING"
    assert body["priority"] == "HIGH"
    publish_task_mock.assert_awaited_once()
    assert len(fake_session.tasks) == 1


def test_create_task_returns_503_when_queue_is_unavailable(client, fake_session) -> None:
    with patch(
        "app.api.routes.tasks.publish_task",
        new=AsyncMock(side_effect=RuntimeError("RabbitMQ is down")),
    ):
        response = client.post(
            "/api/v1/tasks",
            json={
                "title": "Broken task",
                "description": "Queue publish should fail",
                "priority": "LOW",
            },
        )

    assert response.status_code == 503
    assert response.json()["detail"] == "Task queue is unavailable"
    saved_task = next(iter(fake_session.tasks.values()))
    assert saved_task.status == TaskStatus.FAILED
    assert saved_task.error_message == "Failed to publish task to queue"


def test_cancel_task_returns_conflict_for_completed_task(client, fake_session) -> None:
    with patch("app.api.routes.tasks.publish_task", new=AsyncMock()):
        create_response = client.post(
            "/api/v1/tasks",
            json={
                "title": "Completed task",
                "description": "Task to cancel",
                "priority": "MEDIUM",
            },
        )

    task_id = create_response.json()["id"]
    saved_task = next(iter(fake_session.tasks.values()))
    saved_task.status = TaskStatus.COMPLETED

    response = client.delete(f"/api/v1/tasks/{task_id}")

    assert response.status_code == 409
    assert response.json()["detail"] == "Task cannot be cancelled in its current status"


def test_cancel_task_marks_pending_task_cancelled(client, fake_session) -> None:
    with patch("app.api.routes.tasks.publish_task", new=AsyncMock()):
        create_response = client.post(
            "/api/v1/tasks",
            json={
                "title": "Cancelable task",
                "description": "Task to cancel",
                "priority": "MEDIUM",
            },
        )

    task_id = create_response.json()["id"]
    response = client.delete(f"/api/v1/tasks/{task_id}")

    assert response.status_code == 204
    saved_task = next(iter(fake_session.tasks.values()))
    assert saved_task.status == TaskStatus.CANCELLED
    assert saved_task.error_message == "Task was cancelled by user"
