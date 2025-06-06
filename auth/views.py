from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import select, Session

from auth.access_token import AccessToken, create_access_token
from auth.auth_user import authenticate_user
from auth.password import get_password_hash
from data.engine import get_session
from data.service import save_data_to_db, get_data_in_db
from user.dtos import UserCreate
from user.models import User

auth_router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)


@auth_router.post("/register", response_model=AccessToken)
async def register(
        user_create: UserCreate,
        session: Annotated[Session, Depends(get_session)]
):
    get_data_in_db(session, User,
                   mode='query_one',
                   query=select(User).where(User.email == user_create.email),
                   check_existed=True)

    hashed_password = get_password_hash(user_create.password)
    db_user = User.model_validate(user_create, update={"hashed_password": hashed_password})

    save_data_to_db(session, db_user)

    access_token = create_access_token(data={"sub": db_user.email})
    return AccessToken(access_token=access_token, token_type="bearer")


@auth_router.post("/login", response_model=AccessToken)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = authenticate_user(form_data.username, form_data.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.email})
    return AccessToken(access_token=access_token, token_type="bearer")
