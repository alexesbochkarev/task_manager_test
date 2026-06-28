from unittest.mock import AsyncMock, MagicMock, patch


def test_healthcheck_returns_ok(client) -> None:
    connection = AsyncMock()
    context_manager = AsyncMock()
    context_manager.__aenter__.return_value = connection
    context_manager.__aexit__.return_value = None

    engine_mock = MagicMock()
    engine_mock.connect.return_value = context_manager

    with patch("app.main.engine", engine_mock):
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "available"}
