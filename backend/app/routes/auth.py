from sqlmodel import select

from app.db import SessionDep
from app.models import User, UserIn, UserOut, Token
from app.security import CurrentUser, create_token, password_hash
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", status_code=201, response_model=UserOut)
def register(data: UserIn, session: SessionDep):
    existing = session.exec(select(User).where(User.email == data.email)).first()
    if existing is not None:
        raise HTTPException(409, "Email already registered")

    user = User(email=data.email, hashed_password=password_hash.hash(data.password))
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.post("/login", response_model=Token)
def login(form: Annotated[OAuth2PasswordRequestForm, Depends()], session: SessionDep):
    user = session.exec(select(User).where(User.email == form.username)).first()
    if user is None or not password_hash.verify(form.password, user.hashed_password):
        raise HTTPException(401, "Wrong email or password")
    return Token(access_token=create_token(user.id))


@router.get("/me", response_model=UserOut)
def me(user: CurrentUser):
    return user
