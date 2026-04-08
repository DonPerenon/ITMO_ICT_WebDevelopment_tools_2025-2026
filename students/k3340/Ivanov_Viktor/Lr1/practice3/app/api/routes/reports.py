from datetime import date, datetime, time

from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from app.api.deps import get_current_user
from app.db.session import get_session
from app.models import Category, Transaction, TransactionType, User
from app.schemas.reports import CategoryTotal, FinanceSummary

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/summary", response_model=FinanceSummary)
def reports_summary(
    date_from: date | None = None,
    date_to: date | None = None,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> FinanceSummary:
    statement = select(Transaction).where(Transaction.user_id == current_user.id)

    if date_from:
        statement = statement.where(Transaction.occurred_at >= datetime.combine(date_from, time.min))
    if date_to:
        statement = statement.where(Transaction.occurred_at <= datetime.combine(date_to, time.max))

    rows = session.exec(statement).all()

    total_income = float(sum(tx.amount for tx in rows if tx.tx_type == TransactionType.income))
    total_expense = float(sum(tx.amount for tx in rows if tx.tx_type == TransactionType.expense))

    expenses_map: dict[int | None, float] = {}
    for tx in rows:
        if tx.tx_type != TransactionType.expense:
            continue
        expenses_map[tx.category_id] = expenses_map.get(tx.category_id, 0) + float(tx.amount)

    grouped: list[CategoryTotal] = []
    for category_id, total in expenses_map.items():
        if category_id is None:
            grouped.append(CategoryTotal(category_id=None, category_name="No category", total=total))
            continue

        category = session.get(Category, category_id)
        grouped.append(
            CategoryTotal(
                category_id=category_id,
                category_name=category.name if category else "Unknown",
                total=total,
            )
        )

    return FinanceSummary(
        date_from=date_from,
        date_to=date_to,
        total_income=total_income,
        total_expense=total_expense,
        balance=total_income - total_expense,
        expenses_by_category=grouped,
    )
