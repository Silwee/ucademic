from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Response, UploadFile
from sqlmodel import Session, select
from starlette.responses import JSONResponse

from auth.auth_user import get_current_user
from data.engine import engine
from user.models import UserResponse, User, UserUpdateProfile

user_router = APIRouter(
    prefix="/user",
    tags=["user"],
)


@user_router.get("", response_model=UserResponse)
async def read_users_me(current_user: Annotated[User, Depends(get_current_user)]):
    return current_user


@user_router.post("/profile", response_model=UserResponse)
async def update_profile(user_create: UserUpdateProfile, current_user: Annotated[User, Depends(get_current_user)]):
    with Session(engine) as session:
        query = select(User).where(User.id == current_user.id)
        user = session.exec(query).first()
        user.sqlmodel_update(user_create.model_dump(exclude_unset=True))
        session.add(user)
        session.commit()
        session.refresh(user)
        return user


@user_router.get("/me/avatar")
async def get_current_avatar(current_user: Annotated[User, Depends(get_current_user)]) -> Response:
    with Session(engine) as session:
        query = select(User).where(User.id == current_user.id)
        user = session.exec(query).first()

        return Response(
            content=user.avatar,
            media_type=user.avatar_content_type,
        )


@user_router.post("/me/avatar")
async def create_current_avatar(file: UploadFile, current_user: Annotated[User, Depends(get_current_user)]) -> Response:
    with Session(engine) as session:
        query = select(User).where(User.id == current_user.id)
        user = session.exec(query).first()

        file_contents = await file.read()

        user.avatar = file_contents
        user.avatar_content_type = file.content_type
        session.add(user)
        session.commit()

        return JSONResponse(
            content="Upload avatar success!"
        )
