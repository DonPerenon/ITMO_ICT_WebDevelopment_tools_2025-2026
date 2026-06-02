from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.api.deps import get_current_user
from app.db.session import get_session
from app.models import Category, User
from app.schemas.categories import CategoryCreate, CategoryRead, CategoryUpdate

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get("", response_model=list[CategoryRead])
def categories_list(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> list[Category]:
    return session.exec(select(Category).where(Category.user_id == current_user.id)).all()


@router.get("/{category_id}", response_model=CategoryRead)
def categories_get(
    category_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> Category:
    category = session.get(Category, category_id)
    if not category or category.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.post("", response_model=CategoryRead, status_code=201)
def categories_create(
    payload: CategoryCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> Category:
    category = Category(name=payload.name, tx_type=payload.tx_type, user_id=current_user.id)
    session.add(category)
    session.commit()
    session.refresh(category)
    return category


@router.patch("/{category_id}", response_model=CategoryRead)
def categories_update(
    category_id: int,
    payload: CategoryUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> Category:
    category = session.get(Category, category_id)
    if not category or category.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Category not found")

    updates = payload.model_dump(exclude_unset=True)
    for key, value in updates.items():
        setattr(category, key, value)

    session.add(category)
    session.commit()
    session.refresh(category)
    return category


@router.delete("/{category_id}")
def categories_delete(
    category_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> dict[str, bool]:
    category = session.get(Category, category_id)
    if not category or category.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Category not found")

    session.delete(category)
    session.commit()
    return {"ok": True}
