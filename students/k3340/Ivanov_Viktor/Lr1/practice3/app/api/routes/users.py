from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.api.deps import get_current_user
from app.core.security import hash_password, verify_password
from app.db.session import get_session
from app.models import User
from app.schemas.auth import ChangePasswordRequest
from app.schemas.users import UserRead, UserUpdate

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserRead)
def users_me(current_user: User = Depends(get_current_user)) -> User:
    return current_user


@router.get("", response_model=list[UserRead])
def users_list(
    _: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> list[User]:
    return session.exec(select(User)).all()


@router.patch("/me", response_model=UserRead)
def users_update_me(
    payload: UserUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> User:
    updates = payload.model_dump(exclude_unset=True)

    if "username" in updates:
        existing = session.exec(select(User).where(User.username == updates["username"])).first()
        if existing and existing.id != current_user.id:
            raise HTTPException(status_code=409, detail="Username already exists")

    if "email" in updates:
        existing = session.exec(select(User).where(User.email == updates["email"])).first()
        if existing and existing.id != current_user.id:
            raise HTTPException(status_code=409, detail="Email already exists")

    for key, value in updates.items():
        setattr(current_user, key, value)

    session.add(current_user)
    session.commit()
    session.refresh(current_user)
    return current_user


@router.post("/me/change-password")
def users_change_password(
    payload: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> dict[str, str]:
    if not verify_password(payload.old_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Old password is incorrect")

    current_user.hashed_password = hash_password(payload.new_password)
    session.add(current_user)
    session.commit()
    return {"message": "Password changed successfully"}
