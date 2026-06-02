from datetime import date, datetime, time

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.api.deps import get_current_user
from app.db.session import get_session
from app.models import Budget, Category, Transaction, TransactionType, User
from app.schemas.budgets import BudgetCreate, BudgetRead, BudgetUpdate
from app.schemas.categories import CategoryRead

router = APIRouter(prefix="/budgets", tags=["Budgets"])


def _calculate_spent(
    session: Session,
    user_id: int,
    category_id: int,
    period_start: date,
    period_end: date,
) -> float:
    start_dt = datetime.combine(period_start, time.min)
    end_dt = datetime.combine(period_end, time.max)
    expenses = session.exec(
        select(Transaction).where(
            Transaction.user_id == user_id,
            Transaction.category_id == category_id,
            Transaction.tx_type == TransactionType.expense,
            Transaction.occurred_at >= start_dt,
            Transaction.occurred_at <= end_dt,
        )
    ).all()
    return float(sum(tx.amount for tx in expenses))


def _serialize_budget(session: Session, budget: Budget) -> BudgetRead:
    category = session.get(Category, budget.category_id)
    return BudgetRead(
        id=budget.id,
        limit_amount=budget.limit_amount,
        spent_amount=budget.spent_amount,
        period_start=budget.period_start,
        period_end=budget.period_end,
        user_id=budget.user_id,
        category_id=budget.category_id,
        category=(
            CategoryRead(
                id=category.id,
                name=category.name,
                tx_type=category.tx_type,
                user_id=category.user_id,
            )
            if category
            else None
        ),
    )


@router.get("", response_model=list[BudgetRead])
def budgets_list(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> list[BudgetRead]:
    budgets = session.exec(select(Budget).where(Budget.user_id == current_user.id)).all()
    return [_serialize_budget(session, budget) for budget in budgets]


@router.get("/{budget_id}", response_model=BudgetRead)
def budgets_get(
    budget_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> BudgetRead:
    budget = session.get(Budget, budget_id)
    if not budget or budget.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Budget not found")
    return _serialize_budget(session, budget)


@router.post("", response_model=BudgetRead, status_code=201)
def budgets_create(
    payload: BudgetCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> BudgetRead:
    category = session.get(Category, payload.category_id)
    if not category or category.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Category not found")

    if payload.period_end < payload.period_start:
        raise HTTPException(status_code=400, detail="period_end must be >= period_start")

    spent_amount = _calculate_spent(
        session,
        user_id=current_user.id,
        category_id=payload.category_id,
        period_start=payload.period_start,
        period_end=payload.period_end,
    )

    budget = Budget(
        limit_amount=payload.limit_amount,
        spent_amount=spent_amount,
        period_start=payload.period_start,
        period_end=payload.period_end,
        user_id=current_user.id,
        category_id=payload.category_id,
    )
    session.add(budget)
    session.commit()
    session.refresh(budget)
    return _serialize_budget(session, budget)


@router.patch("/{budget_id}", response_model=BudgetRead)
def budgets_update(
    budget_id: int,
    payload: BudgetUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> BudgetRead:
    budget = session.get(Budget, budget_id)
    if not budget or budget.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Budget not found")

    updates = payload.model_dump(exclude_unset=True)
    for key, value in updates.items():
        setattr(budget, key, value)

    if budget.period_end < budget.period_start:
        raise HTTPException(status_code=400, detail="period_end must be >= period_start")

    budget.spent_amount = _calculate_spent(
        session,
        user_id=current_user.id,
        category_id=budget.category_id,
        period_start=budget.period_start,
        period_end=budget.period_end,
    )

    session.add(budget)
    session.commit()
    session.refresh(budget)
    return _serialize_budget(session, budget)


@router.delete("/{budget_id}")
def budgets_delete(
    budget_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> dict[str, bool]:
    budget = session.get(Budget, budget_id)
    if not budget or budget.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Budget not found")

    session.delete(budget)
    session.commit()
    return {"ok": True}


@router.get("/over-limit/list", response_model=list[BudgetRead])
def budgets_over_limit(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> list[BudgetRead]:
    budgets = session.exec(select(Budget).where(Budget.user_id == current_user.id)).all()
    exceeded: list[BudgetRead] = []

    for budget in budgets:
        budget.spent_amount = _calculate_spent(
            session,
            user_id=current_user.id,
            category_id=budget.category_id,
            period_start=budget.period_start,
            period_end=budget.period_end,
        )
        if budget.spent_amount > budget.limit_amount:
            exceeded.append(_serialize_budget(session, budget))

    session.commit()
    return exceeded
