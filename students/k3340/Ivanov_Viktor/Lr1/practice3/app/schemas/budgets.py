from datetime import date

from pydantic import BaseModel, Field

from app.schemas.categories import CategoryRead


class BudgetCreate(BaseModel):
    limit_amount: float = Field(gt=0)
    period_start: date
    period_end: date
    category_id: int


class BudgetUpdate(BaseModel):
    limit_amount: float | None = Field(default=None, gt=0)
    period_start: date | None = None
    period_end: date | None = None


class BudgetRead(BaseModel):
    id: int
    limit_amount: float
    spent_amount: float
    period_start: date
    period_end: date
    user_id: int
    category_id: int
    category: CategoryRead | None = None
