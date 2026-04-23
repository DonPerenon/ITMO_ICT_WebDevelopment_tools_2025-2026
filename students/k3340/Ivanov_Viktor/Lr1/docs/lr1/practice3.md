# Практика 1.3 — Финальная версия

**Стек:** FastAPI, SQLModel, SQLAlchemy, PostgreSQL, Alembic, PyJWT, pydantic-settings

## Что добавлено по сравнению с 1.2

- JWT-аутентификация (Bearer токен)
- Хэширование паролей — `pbkdf2_hmac` + случайная соль (без сторонних библиотек)
- Alembic-миграции вместо `create_all`
- Конфигурация через `.env` (pydantic-settings)
- Новая сущность `Goal` — финансовые цели
- Аналитика: `GET /reports/summary` — доходы / расходы / баланс по периоду
- Все роуты привязаны к `current_user` через dependency

## Зависимости

```
fastapi[all]>=0.115.0
sqlmodel>=0.0.22
SQLAlchemy>=2.0.30
psycopg2-binary>=2.9.9
alembic>=1.13.2
python-dotenv>=1.0.1
pydantic-settings>=2.3.4
PyJWT>=2.9.0
email-validator>=2.2.0
```

## Запуск

```bash
cd practice3
cp .env.example .env        # отредактировать DB_URL и JWT_SECRET
alembic upgrade head        # применить миграции
uvicorn app.main:app --reload
```
