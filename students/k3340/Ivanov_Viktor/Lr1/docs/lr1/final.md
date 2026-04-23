# Финальная сборка

Финальная версия кода — **practice3**.

## Стек

| Компонент | Технология |
|-----------|-----------|
| HTTP-фреймворк | FastAPI |
| ORM | SQLModel + SQLAlchemy |
| БД | PostgreSQL (локально — SQLite) |
| Миграции | Alembic |
| Аутентификация | JWT (PyJWT) + pbkdf2_hmac |
| Конфигурация | pydantic-settings + `.env` |
| Сервер | Uvicorn |

## Запуск

```bash
cd practice3
cp .env.example .env
# Заполнить DB_URL и JWT_SECRET в .env

alembic upgrade head
uvicorn app.main:app --reload --port 8003
```

После запуска доступны:

- API: [http://localhost:8003](http://localhost:8003)
- Swagger UI: [http://localhost:8003/docs](http://localhost:8003/docs)
- ReDoc: [http://localhost:8003/redoc](http://localhost:8003/redoc)

## Пример .env

```env
DB_URL=postgresql://postgres:postgres@localhost/finance_practice3
JWT_SECRET=замените_на_длинную_случайную_строку
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
DB_ECHO=false
AUTO_CREATE_TABLES=false
```
