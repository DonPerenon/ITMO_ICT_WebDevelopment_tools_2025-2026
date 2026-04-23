# Структура проекта

```
practice3/
├── .env                        # переменные окружения (не в git)
├── .env.example                # шаблон
├── alembic.ini                 # конфиг Alembic
├── requirements.txt
├── migrations/
│   ├── env.py                  # читает DB_URL из .env
│   ├── script.py.mako
│   └── versions/
│       └── 20260409_0001_initial_schema.py
└── app/
    ├── main.py                 # точка входа FastAPI, монтирует /api/v1
    ├── models.py               # ORM-модели SQLModel
    ├── db/
    │   └── session.py          # engine + get_session()
    ├── core/
    │   ├── config.py           # pydantic-settings → Settings
    │   └── security.py         # hash_password, verify_password, JWT
    ├── api/
    │   ├── deps.py             # get_current_user() dependency
    │   ├── router.py           # сборный APIRouter
    │   └── routes/
    │       ├── auth.py
    │       ├── users.py
    │       ├── categories.py
    │       ├── tags.py
    │       ├── transactions.py
    │       ├── budgets.py
    │       ├── goals.py
    │       └── reports.py
    └── schemas/
        ├── auth.py
        ├── users.py
        ├── categories.py
        ├── tags.py
        ├── transactions.py
        ├── budgets.py
        ├── goals.py
        └── reports.py
```
