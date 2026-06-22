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

3. Применить миграции:

```bash
docker compose -f docker-compose.local.yml exec backend alembic upgrade head
```

4. Проверить сервис:

```bash
curl http://localhost:8000/health
```
