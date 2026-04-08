from pydantic import BaseModel, Field


class TagCreate(BaseModel):
    name: str = Field(min_length=2, max_length=80)


class TagUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=80)


class TagRead(BaseModel):
    id: int
    name: str
    user_id: int
