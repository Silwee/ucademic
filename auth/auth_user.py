from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jwt import InvalidTokenError
from sqlmodel import Session, select

from config import SECRET_KEY, ALGORITHM
from auth.password import verify_password
from user.models import User
from data.engine import engine

oauth2_scheme = HTTPBearer()


def authenticate_user(email: str, password: str):
    with Session(engine) as session:
        query = select(User).where(User.email == email)
        user = session.exec(query).first()
        if not user:
            return False
        if not verify_password(password, user.hashed_password):
            return False
        return user


async def get_current_user(token: Annotated[HTTPAuthorizationCredentials, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise credentials_exception

    except InvalidTokenError:
        raise credentials_exception

    with Session(engine) as session:
        query = select(User).where(User.email == email)
        user = session.exec(query).first()
        if user is None:
            raise credentials_exception

        return user
