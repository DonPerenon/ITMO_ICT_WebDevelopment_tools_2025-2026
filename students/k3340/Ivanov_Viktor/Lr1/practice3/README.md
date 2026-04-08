# Practice 1.3 — Миграции, ENV, структура проекта, JWT

## Что реализовано
- Структурированный FastAPI-проект (`app/api`, `app/core`, `app/db`, `app/schemas`)
- Модель личных финансов с 7 таблицами:
  - `user`, `category`, `tag`, `transaction`, `transactiontaglink`, `budget`, `goal`
- Связи:
  - `one-to-many`: `user -> categories/tags/transactions/budgets/goals`
  - `many-to-many`: `transaction <-> tag` через `transactiontaglink`
- Ассоциативная сущность с доп. полями: `relevance`, `note`
- Полный CRUD для доменных сущностей
- Вложенные модели в ответах (`transactions`, `budgets`)
- Отчёт `GET /api/v1/reports/summary`
- Проверка превышения бюджета: `GET /api/v1/budgets/over-limit/list`

## Пользовательский функционал (15 баллов)
Реализовано вручную (без библиотек типа `fastapi-users`):
- Регистрация: `POST /api/v1/auth/register`
- Логин + JWT: `POST /api/v1/auth/login`
- JWT-аутентификация для защищённых роутов
- Хэширование паролей через PBKDF2
- Получение профиля: `GET /api/v1/users/me`
- Список пользователей: `GET /api/v1/users`
- Смена пароля: `POST /api/v1/users/me/change-password`

## Настройка `.env`
Скопируйте шаблон и заполните значения:
```bash
cp .env.example .env
```

## Миграции Alembic
Настроено чтение `DB_URL` из `.env` в `migrations/env.py`.

Команды:
```bash
alembic upgrade head
# при изменении моделей
alembic revision --autogenerate -m "describe changes"
alembic upgrade head
```

## Запуск
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 1) Применить миграции
alembic upgrade head

# 2) Запустить API
uvicorn app.main:app --reload
```

Документация: `http://127.0.0.1:8000/docs`
