# Задача 1 и 2. Docker + HTTP-эндпоинт парсера

## Подзадача 1. Упаковка в Docker

### Dockerfile — API (FastAPI Lr1)

```dockerfile
FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y gcc libpq-dev && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app/ app/
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

### Dockerfile — Parser (микросервис парсинга)

```dockerfile
FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y gcc && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV LAB2_DB_PATH=/data/parser.db
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
```

### docker-compose.yml

Управляет пятью сервисами:

```yaml
services:
  db:       # PostgreSQL 16
  redis:    # Redis 7
  api:      # FastAPI :8000
  parser:   # FastAPI-парсер :8001
  worker:   # Celery-воркер
```

Ключевые зависимости:
- `api` ждёт `db` (healthcheck) и `redis`
- `worker` ждёт `redis`

## Подзадача 2. HTTP-эндпоинт парсера в API

Добавлен роутер `app/api/routes/parse.py` с тремя маршрутами.

### POST `/api/v1/parse/sync`

Синхронный вызов парсера — ждёт завершения и возвращает результат:

```
POST /api/v1/parse/sync?url=https://szmetal.ru/catalog/list_goryachekatanyy/
```

Ответ:
```json
{
  "url": "https://szmetal.ru/...",
  "title": "Лист горячекатаный",
  "pages": 1,
  "products": 58
}
```

Поток выполнения:

```
client ──POST /api/v1/parse/sync──▶ api ──POST /parse──▶ parser ──▶ ответ
```

### Реализация (фрагмент `parse.py`)

```python
@router.post("/sync")
def parse_sync(url: str) -> dict:
    response = httpx.post(
        f"{settings.parser_url}/parse",
        params={"url": url},
        timeout=120,
    )
    response.raise_for_status()
    return response.json()
```

### Эндпоинты парсер-сервиса (`parser/main.py`)

| Метод | Путь | Описание |
| --- | --- | --- |
| `GET` | `/` | healthcheck |
| `GET` | `/urls` | список поддерживаемых URL |
| `POST` | `/parse?url=...` | парсить и сохранить в SQLite |

## Конфигурация

Переменные окружения API-сервиса:

| Переменная | Значение по умолчанию |
| --- | --- |
| `DB_URL` | postgresql://... |
| `JWT_SECRET` | — |
| `PARSER_URL` | `http://parser:8001` |
| `CELERY_BROKER_URL` | `redis://redis:6379/0` |
