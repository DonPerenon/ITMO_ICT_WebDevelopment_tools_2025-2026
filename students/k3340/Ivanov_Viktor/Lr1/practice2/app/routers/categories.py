from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.connection import get_session
from app.models import Category, CategoryCreate, CategoryRead, CategoryUpdate, User

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get("", response_model=list[CategoryRead])
def categories_list(session: Session = Depends(get_session)) -> list[Category]:
    return session.exec(select(Category)).all()


@router.get("/{category_id}", response_model=CategoryRead)
def categories_get(category_id: int, session: Session = Depends(get_session)) -> Category:
    category = session.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.post("", response_model=CategoryRead, status_code=201)
def categories_create(payload: CategoryCreate, session: Session = Depends(get_session)) -> Category:
    user = session.get(User, payload.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    category = Category.model_validate(payload)
    session.add(category)
    session.commit()
    session.refresh(category)
    return category


@router.patch("/{category_id}", response_model=CategoryRead)
def categories_update(
    category_id: int,
    payload: CategoryUpdate,
    session: Session = Depends(get_session),
) -> Category:
    category = session.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    updates = payload.model_dump(exclude_unset=True)
    for key, value in updates.items():
        setattr(category, key, value)

    session.add(category)
    session.commit()
    session.refresh(category)
    return category


@router.delete("/{category_id}")
def categories_delete(category_id: int, session: Session = Depends(get_session)) -> dict[str, bool]:
    category = session.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    session.delete(category)
    session.commit()
    return {"ok": True}
