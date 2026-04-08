from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.connection import get_session
from app.models import User, UserCreate, UserRead, UserUpdate

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("", response_model=list[UserRead])
def users_list(session: Session = Depends(get_session)) -> list[User]:
    return session.exec(select(User)).all()


@router.get("/{user_id}", response_model=UserRead)
def users_get(user_id: int, session: Session = Depends(get_session)) -> User:
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("", response_model=UserRead, status_code=201)
def users_create(payload: UserCreate, session: Session = Depends(get_session)) -> User:
    existing_username = session.exec(select(User).where(User.username == payload.username)).first()
    if existing_username:
        raise HTTPException(status_code=409, detail="Username already exists")

    existing_email = session.exec(select(User).where(User.email == payload.email)).first()
    if existing_email:
        raise HTTPException(status_code=409, detail="Email already exists")

    user = User(username=payload.username, email=payload.email, hashed_password=payload.password)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.patch("/{user_id}", response_model=UserRead)
def users_update(user_id: int, payload: UserUpdate, session: Session = Depends(get_session)) -> User:
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    updates = payload.model_dump(exclude_unset=True)
    for key, value in updates.items():
        setattr(user, key, value)

    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.delete("/{user_id}")
def users_delete(user_id: int, session: Session = Depends(get_session)) -> dict[str, bool]:
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    session.delete(user)
    session.commit()
    return {"ok": True}
