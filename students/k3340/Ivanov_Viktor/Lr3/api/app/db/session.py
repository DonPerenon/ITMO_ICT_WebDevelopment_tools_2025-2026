from sqlmodel import Session, SQLModel, create_engine

from app.core.config import settings

engine = create_engine(settings.db_url, echo=settings.db_echo)


def init_db() -> None:
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
