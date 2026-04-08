from pydantic import BaseModel, Field

from app.models import TransactionType


class CategoryCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    tx_type: TransactionType


class CategoryUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=100)
    tx_type: TransactionType | None = None


class CategoryRead(BaseModel):
    id: int
    name: str
    tx_type: TransactionType
    user_id: int
