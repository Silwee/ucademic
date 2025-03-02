from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select

from auth.auth_user import authenticate_user, get_current_user
from auth.password import get_password_hash
from auth.token import Token, create_access_token
from models.User import User, UserResponse, UserCreate
from models.engine import create_db_and_tables, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)


@app.post("/register", response_model=UserResponse)
async def register(user_create: UserCreate):
    user_existed_exception = HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail="User already existed",
    )
    hashed_password = get_password_hash(user_create.password)
    with Session(engine) as session:
        existing_user = session.exec(select(User).where(User.email == user_create.email)).first()
        if existing_user:
            raise user_existed_exception
        db_user = User.model_validate(user_create, update={"hashed_password": hashed_password})
        session.add(db_user)
        session.commit()
        session.refresh(db_user)
        return db_user


@app.post("/login", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.email})
    return Token(access_token=access_token, token_type="bearer")


@app.get("/users/me/", response_model=UserResponse)
async def read_users_me(current_user: Annotated[User, Depends(get_current_user)]):
    return current_user
