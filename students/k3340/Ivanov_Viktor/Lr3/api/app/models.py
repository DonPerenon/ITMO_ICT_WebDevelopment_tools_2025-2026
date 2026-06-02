from datetime import date, datetime
from enum import Enum
from typing import List, Optional

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, Relationship, SQLModel


class TransactionType(str, Enum):
    income = "income"
    expense = "expense"


class GoalStatus(str, Enum):
    active = "active"
    completed = "completed"
    cancelled = "cancelled"


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    email: str = Field(index=True, unique=True)
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    categories: List["Category"] = Relationship(
        back_populates="user", sa_relationship_kwargs={"cascade": "all, delete"}
    )
    tags: List["Tag"] = Relationship(
        back_populates="user", sa_relationship_kwargs={"cascade": "all, delete"}
    )
    transactions: List["Transaction"] = Relationship(
        back_populates="user", sa_relationship_kwargs={"cascade": "all, delete"}
    )
    budgets: List["Budget"] = Relationship(
        back_populates="user", sa_relationship_kwargs={"cascade": "all, delete"}
    )
    goals: List["Goal"] = Relationship(
        back_populates="user", sa_relationship_kwargs={"cascade": "all, delete"}
    )


class Category(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    tx_type: TransactionType
    user_id: int = Field(foreign_key="user.id")

    user: Optional[User] = Relationship(back_populates="categories")
    transactions: List["Transaction"] = Relationship(back_populates="category")
    budgets: List["Budget"] = Relationship(back_populates="category")


class Tag(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    user_id: int = Field(foreign_key="user.id")

    user: Optional[User] = Relationship(back_populates="tags")
    transaction_links: List["TransactionTagLink"] = Relationship(
        back_populates="tag", sa_relationship_kwargs={"cascade": "all, delete"}
    )


class Transaction(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    amount: float = Field(gt=0)
    tx_type: TransactionType
    occurred_at: datetime = Field(default_factory=datetime.utcnow)
    description: Optional[str] = None
    user_id: int = Field(foreign_key="user.id")
    category_id: Optional[int] = Field(default=None, foreign_key="category.id")

    user: Optional[User] = Relationship(back_populates="transactions")
    category: Optional[Category] = Relationship(back_populates="transactions")
    tag_links: List["TransactionTagLink"] = Relationship(
        back_populates="transaction", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )


class TransactionTagLink(SQLModel, table=True):
    transaction_id: Optional[int] = Field(
        default=None, foreign_key="transaction.id", primary_key=True
    )
    tag_id: Optional[int] = Field(default=None, foreign_key="tag.id", primary_key=True)
    relevance: int = Field(default=1, ge=1, le=5)
    note: Optional[str] = None

    transaction: Optional[Transaction] = Relationship(back_populates="tag_links")
    tag: Optional[Tag] = Relationship(back_populates="transaction_links")


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

    user: Optional[User] = Relationship(back_populates="budgets")
    category: Optional[Category] = Relationship(back_populates="budgets")


class Goal(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    target_amount: float = Field(gt=0)
    current_amount: float = Field(default=0, ge=0)
    deadline: Optional[date] = None
    status: GoalStatus = Field(default=GoalStatus.active)
    user_id: int = Field(foreign_key="user.id")

    user: Optional[User] = Relationship(back_populates="goals")
