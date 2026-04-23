# Подключение к БД

## Конфигурация (pydantic-settings)

```python
# app/core/config.py
class Settings(BaseSettings):
    db_url: str
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    db_echo: bool = False
    auto_create_tables: bool = False

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()
```

## Сессия и движок

```python
# app/db/session.py
from sqlmodel import Session, SQLModel, create_engine
from app.core.config import settings

engine = create_engine(settings.db_url, echo=settings.db_echo)

def init_db() -> None:
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
```

`get_session` используется как FastAPI Dependency:

```python
@router.get("/categories")
def list_categories(session: Session = Depends(get_session)):
    ...
```

## Миграции Alembic

Схема применяется через Alembic, а не через `create_all`:

```bash
alembic upgrade head    # применить все миграции
alembic downgrade -1    # откатить последнюю миграцию
```

`migrations/env.py` читает `DB_URL` из `.env`:

```python
from dotenv import load_dotenv
load_dotenv()
config.set_main_option("sqlalchemy.url", os.environ["DB_URL"])
```
