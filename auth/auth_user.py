from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jwt import InvalidTokenError
from sqlmodel import select, Session

from auth.password import verify_password
from config import SECRET_KEY, ALGORITHM
from data.engine import engine
from data.service import get_data_in_db
from user.models import User

oauth2_scheme = HTTPBearer()


def authenticate_user(email: str, password: str):
    with Session(engine) as session:
        user = get_data_in_db(session, User,
                              mode='query_one',
                              query=select(User).where(User.email == email))
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
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
        user = get_data_in_db(session, User,
                              mode='query_one',
                              query=select(User).where(User.email == email))
        if user is None:
            raise credentials_exception

        return user
