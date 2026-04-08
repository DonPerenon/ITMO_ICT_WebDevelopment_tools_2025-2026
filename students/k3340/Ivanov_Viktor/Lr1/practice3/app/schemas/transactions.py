from datetime import datetime

from pydantic import BaseModel, Field

from app.models import TransactionType
from app.schemas.categories import CategoryRead


class TransactionTagAssign(BaseModel):
    tag_id: int
    relevance: int = Field(default=1, ge=1, le=5)
    note: str | None = None


class TransactionCreate(BaseModel):
    title: str = Field(min_length=2, max_length=120)
    amount: float = Field(gt=0)
    tx_type: TransactionType
    occurred_at: datetime | None = None
    description: str | None = None
    category_id: int | None = None
    tags: list[TransactionTagAssign] = []


class TransactionUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=2, max_length=120)
    amount: float | None = Field(default=None, gt=0)
    tx_type: TransactionType | None = None
    occurred_at: datetime | None = None
    description: str | None = None
    category_id: int | None = None
    tags: list[TransactionTagAssign] | None = None


class TagWithMeta(BaseModel):
    id: int
    name: str
    relevance: int
    note: str | None = None


class TransactionRead(BaseModel):
    id: int
    title: str
    amount: float
    tx_type: TransactionType
    occurred_at: datetime
    description: str | None = None
    user_id: int
    category_id: int | None = None
    category: CategoryRead | None = None
    tags: list[TagWithMeta] = []
