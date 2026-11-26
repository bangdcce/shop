from app.config import settings
from app.db import SessionDep
from app.models import User
from datetime import datetime, UTC, timedelta
import jwt
from typing import Annotated
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def create_token(user_id: int) -> str:
    expires = datetime.now(UTC) + timedelta(minutes=settings.token_minutes)
    return jwt.encode(
        {"sub": str(user_id), "exp": expires}, settings.secret_key, algorithm="HS256"
    )


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)], session: SessionDep
) -> User:
    error = HTTPException(
        401, "Could not validate credentials", headers={"WWW-Authenticate": "Bearer"}
    )
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
        user_id = int(payload["sub"])
    except (jwt.InvalidTokenError, KeyError, ValueError):
        raise error
    user = session.get(User, user_id)
    if user is None:
        raise error
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
