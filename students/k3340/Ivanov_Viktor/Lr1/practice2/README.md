# Practice 1.2 — SQLModel + PostgreSQL

## Что реализовано
- Подключение к PostgreSQL (`app/connection.py`)
- ORM-модели SQLModel (6 таблиц):
  - `user`, `category`, `tag`, `transaction`, `budget`, `transactiontaglink`
- Связи:
  - `one-to-many`: пользователь -> транзакции/категории/бюджеты
  - `many-to-many`: транзакции <-> теги через `TransactionTagLink`
- Ассоциативная сущность содержит дополнительные поля: `priority`, `note`
- CRUD API для пользователей, категорий, тегов, транзакций, бюджетов
- Вложенный вывод связей в `GET /transactions` и `GET /transactions/{id}`

## Запуск
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

export DB_URL="postgresql://postgres:postgres@localhost/finance_practice2"
uvicorn app.main:app --reload
```

Документация: `http://127.0.0.1:8000/docs`
