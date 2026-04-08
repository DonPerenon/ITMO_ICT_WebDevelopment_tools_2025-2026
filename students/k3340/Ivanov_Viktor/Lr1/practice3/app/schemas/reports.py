from datetime import date

from pydantic import BaseModel


class CategoryTotal(BaseModel):
    category_id: int | None
    category_name: str
    total: float


class FinanceSummary(BaseModel):
    date_from: date | None
    date_to: date | None
    total_income: float
    total_expense: float
    balance: float
    expenses_by_category: list[CategoryTotal]
