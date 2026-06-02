# Лабораторная работа №3 — Docker, парсер и очереди

**Дисциплина:** Инструментальные средства веб-разработки  
**Тема:** Docker, интеграция FastAPI с парсером и очередью задач  

## Цель работы

Упаковать FastAPI-приложение (ЛР1) и парсер (ЛР2) в Docker-контейнеры, объединить их через Docker Compose, организовать вызов парсера по HTTP и асинхронную обработку через очередь задач Celery + Redis.

## Архитектура

```
                          ┌────────┐
                          │ client │
                          └───┬────┘
                              │ HTTP
                         ┌────▼─────┐
                         │   api    │ :8000  (FastAPI Lr1 + /parse/*)
                         └────┬─────┘
              ┌───────────────┼──────────────┐
              │ HTTP sync     │ Celery task  │
         ┌────▼────┐    ┌─────▼────┐   ┌────▼────┐
         │ parser  │    │  redis   │   │ worker  │
         │ :8001   │    │  :6379   │   │ (Celery)│
         └────┬────┘    └──────────┘   └────┬────┘
              │                             │
              └────────────┬────────────────┘
                           │ SQLite
                      ┌────▼────┐
                      │ parser  │
                      │   .db   │
                      └─────────┘

    ┌──────┐ PostgreSQL
    │  db  │ :5432  ← api
    └──────┘
```

## Сервисы Docker Compose

| Сервис | Образ / Build | Порт | Назначение |
| --- | --- | --- | --- |
| `db` | `postgres:16-alpine` | 5432 | PostgreSQL для основного API |
| `redis` | `redis:7-alpine` | 6379 | Брокер задач Celery |
| `api` | `./api` | **8000** | FastAPI из ЛР1 + эндпоинты парсера |
| `parser` | `./parser` | **8001** | Микросервис парсинга |
| `worker` | `./parser` | — | Celery-воркер |

## Структура проекта

```
Lr3/
├── .env
├── .env.example
├── docker-compose.yml
├── api/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── main.py
│       ├── models.py
│       ├── core/config.py      ← + PARSER_URL, CELERY_*
│       ├── db/session.py
│       ├── schemas/
│       └── api/
│           ├── router.py
│           └── routes/
│               ├── ...         ← маршруты из ЛР1
│               └── parse.py    ← NEW: /parse/sync, /parse/async, /parse/result
└── parser/
    ├── Dockerfile
    ├── requirements.txt
    ├── main.py         ← FastAPI /parse
    ├── tasks.py        ← Celery task parse_url
    ├── parser_utils.py ← из ЛР2
    └── db.py           ← из ЛР2
```

## Задачи

| Задача | Описание | Баллы |
| --- | --- | --- |
| [Задача 1+2](task1.md) | Docker + HTTP-эндпоинт парсера | 70% |
| [Задача 3](task2.md) | Celery + Redis + async эндпоинт | 100% |

## Быстрый старт

```bash
cd Lr3
cp .env.example .env    # при необходимости отредактировать
docker compose up --build
```

Сервисы:

- Swagger API: [http://localhost:8000/docs](http://localhost:8000/docs)
- Swagger Parser: [http://localhost:8001/docs](http://localhost:8001/docs)

## Ссылки

- [Код ЛР3 на GitHub](https://github.com/DonPerenon/ITMO_ICT_WebDevelopment_tools_2025-2026/tree/main/students/k3340/Ivanov_Viktor/Lr3)
