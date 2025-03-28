from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import select

from auth.access_token import AccessToken, create_access_token
from auth.auth_user import authenticate_user
from auth.password import get_password_hash
from data.query import run_sql_select_query, run_sql_save_query
from user.dtos import UserCreate
from user.models import User

auth_router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)


@auth_router.post("/register", response_model=AccessToken)
async def register(user_create: UserCreate):
    hashed_password = get_password_hash(user_create.password)

    query = select(User).where(User.email == user_create.email)
    existing_user = run_sql_select_query(query, mode="one")

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already existed",
        )

    db_user = User.model_validate(user_create, update={"hashed_password": hashed_password})
    db_user = run_sql_save_query(db_user)

    access_token = create_access_token(data={"sub": db_user.email})
    return AccessToken(access_token=access_token, token_type="bearer")


@auth_router.post("/login", response_model=AccessToken)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.email})
    return AccessToken(access_token=access_token, token_type="bearer")