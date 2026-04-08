from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class TransactionType(str, Enum):
    income = "income"
    expense = "expense"


class Category(BaseModel):
    id: int
    name: str
    tx_type: TransactionType


class Tag(BaseModel):
    id: int
    name: str


class Transaction(BaseModel):
    id: int
    title: str
    amount: float = Field(gt=0)
    tx_type: TransactionType
    category: Category
    tags: list[Tag] = []
    comment: Optional[str] = None


class TransactionCreate(BaseModel):
    title: str
    amount: float = Field(gt=0)
    tx_type: TransactionType
    category_id: int
    tag_ids: list[int] = []
    comment: Optional[str] = None


class TransactionUpdate(BaseModel):
    title: Optional[str] = None
    amount: Optional[float] = Field(default=None, gt=0)
    tx_type: Optional[TransactionType] = None
    category_id: Optional[int] = None
    tag_ids: Optional[list[int]] = None
    comment: Optional[str] = None


class CategoryCreate(BaseModel):
    name: str
    tx_type: TransactionType
