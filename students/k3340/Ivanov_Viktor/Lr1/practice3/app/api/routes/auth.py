from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select

from app.core.security import create_access_token, hash_password, verify_password
from app.db.session import get_session
from app.models import User
from app.schemas.auth import RegisterRequest, Token
from app.schemas.users import UserRead

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=UserRead, status_code=201)
def register(payload: RegisterRequest, session: Session = Depends(get_session)) -> User:
    existing_by_username = session.exec(select(User).where(User.username == payload.username)).first()
    if existing_by_username:
        raise HTTPException(status_code=409, detail="Username already exists")

    existing_by_email = session.exec(select(User).where(User.email == payload.email)).first()
    if existing_by_email:
        raise HTTPException(status_code=409, detail="Email already exists")

    user = User(
        username=payload.username,
        email=payload.email,
        hashed_password=hash_password(payload.password),
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
) -> Token:
    user = session.exec(select(User).where(User.username == form_data.username)).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(subject=str(user.id))
    return Token(access_token=access_token)
