from __future__ import annotations

import os
from datetime import datetime
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlmodel import Field, Session, SQLModel, create_engine

DB_PATH = os.getenv(
    "LAB2_DB_PATH",
    os.path.join(os.path.dirname(__file__), "lab2_parser.db"),
)
DB_URL = f"sqlite:///{DB_PATH}"
ASYNC_DB_URL = f"sqlite+aiosqlite:///{DB_PATH}"


class ParsedPage(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    url: str = Field(index=True)
    title: str
    fetched_at: datetime = Field(default_factory=datetime.utcnow)


class MetalPrice(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    page_id: int = Field(foreign_key="parsedpage.id")
    name: str
    kind: Optional[str] = None
    size: Optional[str] = None
    steel_grade: Optional[str] = None
    characteristics: Optional[str] = None
    manufacturer: Optional[str] = None
    warehouse: Optional[str] = None
    price_text: str
    price_value: Optional[float] = None


engine = create_engine(
    DB_URL,
    echo=False,
    connect_args={"check_same_thread": False},
)

async_engine = create_async_engine(ASYNC_DB_URL, echo=False)


def init_db() -> None:
    SQLModel.metadata.create_all(engine)


async def init_db_async() -> None:
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


def get_session() -> Session:
    return Session(engine)


def get_async_session() -> AsyncSession:
    return AsyncSession(async_engine)
