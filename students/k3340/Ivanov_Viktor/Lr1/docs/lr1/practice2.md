# Практика 1.2 — PostgreSQL + SQLModel

**Стек:** FastAPI, SQLModel, SQLAlchemy, PostgreSQL, psycopg2

## Что добавлено по сравнению с 1.1

- Реальная БД (PostgreSQL) — данные сохраняются между перезапусками
- Сущность `User` — таблица пользователей
- Связи `one-to-many`: User → Category, Tag, Transaction, Budget
- Связь `many-to-many`: Transaction ↔ Tag через `TransactionTagLink`
- Ассоциативная таблица `TransactionTagLink` с доп. полями (`priority`, `note`)
- Сущность `Budget` — бюджеты по категориям

## Ключевые файлы

| Файл | Назначение |
|------|-----------|
| `app/models.py` | SQLModel-таблицы + схемы Read/Create/Update |
| `app/connection.py` | `create_engine`, `init_db()`, `get_session()` |
| `app/main.py` | Регистрация роутеров, `init_db()` при старте |
| `app/routers/users.py` | CRUD пользователей |
| `app/routers/categories.py` | CRUD категорий |
| `app/routers/tags.py` | CRUD тегов |
| `app/routers/transactions.py` | CRUD транзакций + сериализация тегов через join |
| `app/routers/budgets.py` | CRUD бюджетов |

## Подключение к БД

```python
DB_URL = os.getenv("DB_URL", "postgresql://postgres:postgres@localhost/finance_practice2")
engine = create_engine(DB_URL, echo=True)

def init_db() -> None:
    SQLModel.metadata.create_all(engine)
```

## Особенности

- Нет аутентификации: `user_id` передаётся в теле запроса
- Схемы разделены: `*Create`, `*Update`, `*Read`
- `TransactionTagLink` хранит `priority` (1–5) и `note`
