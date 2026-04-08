# Practice 1.1 — Базовое FastAPI-приложение (личные финансы)

## Что реализовано
- Базовый FastAPI сервер
- Временная БД в памяти (`transactions`, `categories`, `tags`)
- CRUD для транзакций
- API для вложенного объекта `Category`
- Pydantic-модели и аннотации типов

## Запуск
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Проверка:
- `http://127.0.0.1:8000/`
- `http://127.0.0.1:8000/docs`
