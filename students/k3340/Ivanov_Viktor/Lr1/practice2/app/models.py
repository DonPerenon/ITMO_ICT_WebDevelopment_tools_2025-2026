from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import Optional

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, SQLModel


class TransactionType(str, Enum):
    income = "income"
    expense = "expense"


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    email: str = Field(index=True, unique=True)
    hashed_password: str = Field(default="not_used_in_practice2")


class Category(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    tx_type: TransactionType
    user_id: int = Field(foreign_key="user.id")


class Tag(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    user_id: int = Field(foreign_key="user.id")


class Transaction(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    amount: float = Field(gt=0)
    tx_type: TransactionType
    occurred_at: datetime = Field(default_factory=datetime.utcnow)
    description: Optional[str] = None
    user_id: int = Field(foreign_key="user.id")
    category_id: Optional[int] = Field(default=None, foreign_key="category.id")


class TransactionTagLink(SQLModel, table=True):
    transaction_id: Optional[int] = Field(
        default=None, foreign_key="transaction.id", primary_key=True
    )
    tag_id: Optional[int] = Field(default=None, foreign_key="tag.id", primary_key=True)
    priority: int = Field(default=1, ge=1, le=5)
    note: Optional[str] = None


class Budget(SQLModel, table=True):
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "category_id",
            "period_start",
            "period_end",
            name="uq_budget_period",
        ),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    limit_amount: float = Field(gt=0)
    spent_amount: float = Field(default=0, ge=0)
    period_start: date
    period_end: date
    user_id: int = Field(foreign_key="user.id")
    category_id: int = Field(foreign_key="category.id")


class UserCreate(SQLModel):
    username: str
    email: str
    password: str


class UserUpdate(SQLModel):
    username: Optional[str] = None
    email: Optional[str] = None


class UserRead(SQLModel):
    id: int
    username: str
    email: str


class CategoryCreate(SQLModel):
    name: str
    tx_type: TransactionType
    user_id: int


class CategoryUpdate(SQLModel):
    name: Optional[str] = None
    tx_type: Optional[TransactionType] = None


class CategoryRead(SQLModel):
    id: int
    name: str
    tx_type: TransactionType
    user_id: int


class TagCreate(SQLModel):
    name: str
    user_id: int


class TagUpdate(SQLModel):
    name: Optional[str] = None


class TagRead(SQLModel):
    id: int
    name: str
    user_id: int


class TransactionTagAssign(SQLModel):
    tag_id: int
    priority: int = Field(default=1, ge=1, le=5)
    note: Optional[str] = None


class TransactionCreate(SQLModel):
    title: str
    amount: float = Field(gt=0)
    tx_type: TransactionType
    occurred_at: Optional[datetime] = None
    description: Optional[str] = None
    user_id: int
    category_id: Optional[int] = None
    tag_links: list[TransactionTagAssign] = []


class TransactionUpdate(SQLModel):
    title: Optional[str] = None
    amount: Optional[float] = Field(default=None, gt=0)
    tx_type: Optional[TransactionType] = None
    occurred_at: Optional[datetime] = None
    description: Optional[str] = None
    category_id: Optional[int] = None
    tag_links: Optional[list[TransactionTagAssign]] = None


class TransactionTagRead(SQLModel):
    tag: TagRead
    priority: int
    note: Optional[str] = None


class TransactionRead(SQLModel):
    id: int
    title: str
    amount: float
    tx_type: TransactionType
    occurred_at: datetime
    description: Optional[str] = None
    user_id: int
    category_id: Optional[int] = None
    category: Optional[CategoryRead] = None
    tags: list[TransactionTagRead] = []


class BudgetCreate(SQLModel):
    limit_amount: float = Field(gt=0)
    period_start: date
    period_end: date
    user_id: int
    category_id: int


class BudgetUpdate(SQLModel):
    limit_amount: Optional[float] = Field(default=None, gt=0)
    spent_amount: Optional[float] = Field(default=None, ge=0)
    period_start: Optional[date] = None
    period_end: Optional[date] = None


class BudgetRead(SQLModel):
    id: int
    limit_amount: float
    spent_amount: float
    period_start: date
    period_end: date
    user_id: int
    category_id: int
