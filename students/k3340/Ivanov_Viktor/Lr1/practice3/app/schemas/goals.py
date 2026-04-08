from datetime import date

from pydantic import BaseModel, Field

from app.models import GoalStatus


class GoalCreate(BaseModel):
    title: str = Field(min_length=2, max_length=120)
    target_amount: float = Field(gt=0)
    current_amount: float = Field(default=0, ge=0)
    deadline: date | None = None


class GoalUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=2, max_length=120)
    target_amount: float | None = Field(default=None, gt=0)
    current_amount: float | None = Field(default=None, ge=0)
    deadline: date | None = None
    status: GoalStatus | None = None


class GoalRead(BaseModel):
    id: int
    title: str
    target_amount: float
    current_amount: float
    deadline: date | None
    status: GoalStatus
    user_id: int
