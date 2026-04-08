# Отчет по ЛР1

Дисциплина: Инструментальные средства веб-разработки  
Тема: Реализация серверного приложения FastAPI (вариант: сервис личных финансов)

## Ссылки на GitHub
- Репозиторий: <https://github.com/DonPerenon/ITMO_ICT_WebDevelopment_tools_2025-2026>
- Ветка с работой: <https://github.com/DonPerenon/ITMO_ICT_WebDevelopment_tools_2025-2026/tree/main>
- Папка ЛР1: <https://github.com/DonPerenon/ITMO_ICT_WebDevelopment_tools_2025-2026/tree/main/students/k3340/Ivanov_Viktor/Lr1>
- Практика 1.1: <https://github.com/DonPerenon/ITMO_ICT_WebDevelopment_tools_2025-2026/tree/main/students/k3340/Ivanov_Viktor/Lr1/practice1>
- Практика 1.2: <https://github.com/DonPerenon/ITMO_ICT_WebDevelopment_tools_2025-2026/tree/main/students/k3340/Ivanov_Viktor/Lr1/practice2>
- Практика 1.3 (финальная версия): <https://github.com/DonPerenon/ITMO_ICT_WebDevelopment_tools_2025-2026/tree/main/students/k3340/Ivanov_Viktor/Lr1/practice3>

## Реализованные практики
- Практика 1.1: базовое FastAPI-приложение, временная БД, CRUD, Pydantic-модели.
- Практика 1.2: PostgreSQL + SQLModel, связи one-to-many и many-to-many, ассоциативная таблица с дополнительными полями.
- Практика 1.3: структура проекта, Alembic-миграции, `.env`, JWT-аутентификация, хэширование паролей, пользовательские API.

## Финальная структура проекта
Финальная версия кода представлена в `practice3`:
- `app/main.py` — точка входа FastAPI
- `app/models.py` — ORM-модели SQLModel
- `app/db/session.py` — подключение к БД и сессии
- `app/core/config.py` — конфигурация через `.env`
- `app/core/security.py` — ручные JWT и хэширование паролей
- `app/api/routes/*.py` — роутеры API
- `migrations/*` — Alembic-конфигурация и миграции

## Модели данных (финальная версия)
Основные таблицы (SQLModel):
- `User`
- `Category`
- `Tag`
- `Transaction`
- `TransactionTagLink` (ассоциативная many-to-many сущность)
- `Budget`
- `Goal`

Связи:
- `one-to-many`: `User -> Category/Tag/Transaction/Budget/Goal`
- `many-to-many`: `Transaction <-> Tag` через `TransactionTagLink`

Дополнительные поля в ассоциативной сущности:
- `TransactionTagLink.relevance`
- `TransactionTagLink.note`

## Код подключения к БД
Источник: `practice3/app/db/session.py` и `practice3/app/core/config.py`.

```python
# app/core/config.py
class Settings(BaseSettings):
    db_url: str
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    db_echo: bool = False
    auto_create_tables: bool = False
```

```python
# app/db/session.py
engine = create_engine(settings.db_url, echo=settings.db_echo)


def init_db() -> None:
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
```

Переменные окружения задаются через `.env` (`.env.example` приложен в `practice3`).

## Реализованные эндпоинты (финальная версия `practice3`)
Базовый роут:
- `GET /` — проверка доступности сервиса

Префикс API: `/api/v1`

### Auth
- `POST /api/v1/auth/register` — регистрация
- `POST /api/v1/auth/login` — получение JWT токена

### Users
- `GET /api/v1/users/me` — информация о текущем пользователе
- `GET /api/v1/users` — список пользователей
- `PATCH /api/v1/users/me` — обновление профиля
- `POST /api/v1/users/me/change-password` — смена пароля

### Categories
- `GET /api/v1/categories`
- `GET /api/v1/categories/{category_id}`
- `POST /api/v1/categories`
- `PATCH /api/v1/categories/{category_id}`
- `DELETE /api/v1/categories/{category_id}`

### Tags
- `GET /api/v1/tags`
- `GET /api/v1/tags/{tag_id}`
- `POST /api/v1/tags`
- `PATCH /api/v1/tags/{tag_id}`
- `DELETE /api/v1/tags/{tag_id}`

### Transactions
- `GET /api/v1/transactions`
- `GET /api/v1/transactions/{transaction_id}`
- `POST /api/v1/transactions`
- `PATCH /api/v1/transactions/{transaction_id}`
- `DELETE /api/v1/transactions/{transaction_id}`

### Budgets
- `GET /api/v1/budgets`
- `GET /api/v1/budgets/{budget_id}`
- `POST /api/v1/budgets`
- `PATCH /api/v1/budgets/{budget_id}`
- `DELETE /api/v1/budgets/{budget_id}`
- `GET /api/v1/budgets/over-limit/list` — бюджеты с превышением лимита

### Goals
- `GET /api/v1/goals`
- `GET /api/v1/goals/{goal_id}`
- `POST /api/v1/goals`
- `PATCH /api/v1/goals/{goal_id}`
- `DELETE /api/v1/goals/{goal_id}`

### Reports
- `GET /api/v1/reports/summary` — финансовый отчёт (доходы/расходы/баланс/группировка)

## Миграции Alembic
- Конфиг: `practice3/alembic.ini`
- Окружение: `practice3/migrations/env.py`
- Начальная миграция: `practice3/migrations/versions/20260409_0001_initial_schema.py`

В `migrations/env.py` реализовано чтение `DB_URL` из `.env`.

## Аутентификация и безопасность
Реализовано вручную (без `fastapi-users`):
- генерация JWT (`PyJWT`)
- проверка JWT в dependency
- хэширование паролей (`pbkdf2_hmac` + salt)
- проверка паролей через `hmac.compare_digest`

## Проверка требований
- 5+ таблиц: выполнено (7 таблиц)
- Связи one-to-many: выполнено
- Связи many-to-many: выполнено
- Ассоциативная сущность с доп. полями: выполнено (`TransactionTagLink`)
- CRUD API: выполнено
- Вложенные модели в GET: выполнено (`transactions`, `budgets`)
- PostgreSQL + SQLModel: выполнено
- Alembic миграции: выполнено
- `.env` + `.gitignore`: выполнено
- JWT/регистрация/авторизация/смена пароля: выполнено
