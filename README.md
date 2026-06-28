# task_manager_test

## Запуск

1. Создать `.env` на основе примера:

```bash
cp .env.example .env
```

2. Поднять контейнеры:

```bash
docker compose -f docker-compose.local.yml up --build
```

Будут запущены сервисы:
- `backend`
- `db`
- `rabbitmq`
- `worker`

3. Применить миграции:

```bash
docker compose -f docker-compose.local.yml exec backend alembic upgrade head
```

4. Проверить сервис:

```bash
curl http://localhost:8000/health
```

## Тесты

Установить зависимости:

```bash
pip install -r requirements.txt
```

Запустить тесты:

```bash
python -m pytest tests -q
```

## Проверка задач

Создать задачу:

```bash
curl -X POST http://localhost:8000/api/v1/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Test task", "description": "Run async processing", "priority": "HIGH"}'
```

Проверить список задач:

```bash
curl http://localhost:8000/api/v1/tasks
```

После создания задача должна пройти путь:
- `PENDING`
- `IN_PROGRESS`
- `COMPLETED`

RabbitMQ management доступен по адресу:

```text
http://localhost:15672
```
