import os

from sqlmodel import Session, SQLModel, create_engine

DB_URL = os.getenv("DB_URL", "postgresql://postgres:postgres@localhost/finance_practice2")

engine = create_engine(DB_URL, echo=True)


def init_db() -> None:
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
