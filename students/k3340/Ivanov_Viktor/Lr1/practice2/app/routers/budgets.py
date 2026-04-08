from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.connection import get_session
from app.models import Budget, BudgetCreate, BudgetRead, BudgetUpdate, Category, User

router = APIRouter(prefix="/budgets", tags=["Budgets"])


@router.get("", response_model=list[BudgetRead])
def budgets_list(session: Session = Depends(get_session)) -> list[Budget]:
    return session.exec(select(Budget)).all()


@router.get("/{budget_id}", response_model=BudgetRead)
def budgets_get(budget_id: int, session: Session = Depends(get_session)) -> Budget:
    budget = session.get(Budget, budget_id)
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    return budget


@router.post("", response_model=BudgetRead, status_code=201)
def budgets_create(payload: BudgetCreate, session: Session = Depends(get_session)) -> Budget:
    user = session.get(User, payload.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    category = session.get(Category, payload.category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    if category.user_id != payload.user_id:
        raise HTTPException(status_code=400, detail="Category does not belong to user")

    if payload.period_end < payload.period_start:
        raise HTTPException(status_code=400, detail="period_end must be >= period_start")

    budget = Budget.model_validate(payload)
    session.add(budget)
    session.commit()
    session.refresh(budget)
    return budget


@router.patch("/{budget_id}", response_model=BudgetRead)
def budgets_update(
    budget_id: int,
    payload: BudgetUpdate,
    session: Session = Depends(get_session),
) -> Budget:
    budget = session.get(Budget, budget_id)
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")

    updates = payload.model_dump(exclude_unset=True)
    for key, value in updates.items():
        setattr(budget, key, value)

    if budget.period_end < budget.period_start:
        raise HTTPException(status_code=400, detail="period_end must be >= period_start")

    session.add(budget)
    session.commit()
    session.refresh(budget)
    return budget


@router.delete("/{budget_id}")
def budgets_delete(budget_id: int, session: Session = Depends(get_session)) -> dict[str, bool]:
    budget = session.get(Budget, budget_id)
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")

    session.delete(budget)
    session.commit()
    return {"ok": True}
