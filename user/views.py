from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile
from sqlmodel import select

from auth.auth_user import get_current_user
from data.aws import s3_client, bucket_name, cloudfront_url
from user.dtos import UserResponse, UserUpdateProfile
from user.models import User
from data.query import run_sql_select_query, run_sql_save_query

user_router = APIRouter(
    prefix="/user",
    tags=["user"],
)


@user_router.get("", response_model=UserResponse)
async def read_users_me(current_user: Annotated[User, Depends(get_current_user)]):
    return current_user


@user_router.get("/{user_id}/profile",
                 responses={
                     200: {"model": UserResponse},
                     404: {"description": "User not found"},
                 })
async def get_user_profile(user_id: UUID):
    query = select(User).where(User.id == user_id)
    user = run_sql_select_query(query, mode="one")
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user


@user_router.post("/profile", response_model=UserResponse)
async def update_my_profile(user_create: UserUpdateProfile, current_user: Annotated[User, Depends(get_current_user)]):
    query = select(User).where(User.id == current_user.id)
    user = run_sql_select_query(query, mode="one")

    # Use sqlmodel_update for update, model_validate for create
    user.sqlmodel_update(user_create.model_dump(exclude_unset=True))
    return run_sql_save_query(user)


@user_router.post("/me/avatar", response_model=UserResponse)
async def upload_current_user_avatar(file: UploadFile, current_user: Annotated[User, Depends(get_current_user)]):
    query = select(User).where(User.id == current_user.id)
    user = run_sql_select_query(query, mode="one")

    filename = 'user/' + user.id.__str__()

    s3_client.upload_fileobj(Fileobj=file.file,
                             Bucket=bucket_name,
                             Key=filename,
                             ExtraArgs={'ContentType': file.content_type}
                             )

    user.avatar_link = cloudfront_url + filename
    return run_sql_save_query(user)
