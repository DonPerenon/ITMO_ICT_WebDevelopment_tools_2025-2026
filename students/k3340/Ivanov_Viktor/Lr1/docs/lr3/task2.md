# Задача 3. Celery + Redis — асинхронный парсинг

## Как работает очередь

```
client
  │
  ▼ POST /api/v1/parse/async?url=...
api (FastAPI)
  │  celery_app.send_task("parser.tasks.parse_url", args=[url])
  ▼
Redis (брокер)  ←──── задача в очереди "parse"
  │
  ▼
worker (Celery) ──── выполняет parse_url(url)
  │  сохраняет результат в Redis backend
  ▼
Redis (backend)

client ──▶ GET /api/v1/parse/result/{task_id} ──▶ api ──▶ Redis ──▶ результат
```

## Настройка Celery

### В сервисе `api` (`parse.py`)

```python
celery_app = Celery(
    "api_worker",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)
```

API только **ставит задачу в очередь** — не выполняет её:

```python
@router.post("/async")
def parse_async(url: str) -> dict:
    task = celery_app.send_task(
        "parser.tasks.parse_url", args=[url], queue="parse"
    )
    return {"task_id": task.id, "status": "queued"}
```

### В сервисе `worker` (`tasks.py`)

```python
@celery_app.task(name="parser.tasks.parse_url", bind=True)
def parse_url(self, url: str) -> dict:
    pages_html = fetch_all_pages(url)
    ...
    return {"url": url, "title": title, "products": len(products)}
```

Воркер запускается командой:
```bash
celery -A tasks worker --loglevel=info -Q parse --concurrency=2
```

## Эндпоинты

### POST `/api/v1/parse/async`

```
POST /api/v1/parse/async?url=https://szmetal.ru/catalog/list_goryachekatanyy/
```

Немедленный ответ:
```json
{"task_id": "abc-123", "status": "queued"}
```

### GET `/api/v1/parse/result/{task_id}`

Опрос результата:

```
GET /api/v1/parse/result/abc-123
```

Пока задача выполняется:
```json
{"task_id": "abc-123", "status": "pending"}
```

После завершения:
```json
{
  "task_id": "abc-123",
  "status": "success",
  "result": {"url": "...", "title": "...", "products": 58}
}
```

## Сравнение подходов

| | Sync (`/parse/sync`) | Async (`/parse/async`) |
| --- | --- | --- |
| Клиент ждёт ответа | Да — пока идёт парсинг | Нет — сразу получает `task_id` |
| Подходит для | Быстрых запросов | Долгих/ненадёжных парсингов |
| Масштабирование | Ограничено воркерами | Горизонтальное (много воркеров) |

## Docker Compose для задачи 3

В `docker-compose.yml` добавлены:

```yaml
  redis:
    image: redis:7-alpine

  worker:
    build: ./parser
    command: celery -A tasks worker --loglevel=info -Q parse --concurrency=2
    depends_on:
      redis:
        condition: service_healthy
```

Масштабирование воркеров:
```bash
docker compose up --scale worker=3
```
