from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select

from auth.access_token import AccessToken, create_access_token
from auth.auth_user import authenticate_user
from auth.password import get_password_hash
from user.models import UserCreate, User
from data.engine import engine

auth_router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)


@auth_router.post("/register", response_model=AccessToken)
async def register(user_create: UserCreate):
    hashed_password = get_password_hash(user_create.password)
    with Session(engine) as session:
        query = select(User).where(User.email == user_create.email)
        existing_user = session.exec(query).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User already existed",
            )
        db_user = User.model_validate(user_create, update={"hashed_password": hashed_password})
        session.add(db_user)
        session.commit()
        session.refresh(db_user)
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