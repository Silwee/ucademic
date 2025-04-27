from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, UploadFile
from sqlmodel import Session

from auth.auth_user import get_current_user
from data.aws import s3_client, bucket_name, cloudfront_url
from data.engine import get_session
from data.service import get_data_in_db, save_data_to_db
from user.dtos import UserResponse, UserUpdateProfile
from user.models import User

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
async def get_user_profile(
        user_id: UUID,
        session: Annotated[Session, Depends(get_session)]
):
    return get_data_in_db(session, User,
                          obj_id=user_id,
                          dto=UserResponse,
                          check_not_found=True)


@user_router.put("/profile", response_model=UserResponse)
async def update_my_profile(
        user_create: UserUpdateProfile,
        current_user: Annotated[User, Depends(get_current_user)],
        session: Annotated[Session, Depends(get_session)]
):
    # Use sqlmodel_update for update, model_validate for create
    current_user.sqlmodel_update(user_create.model_dump(exclude_unset=True))
    return save_data_to_db(session, current_user, dto=UserResponse)


@user_router.post("/me/avatar", response_model=UserResponse)
async def upload_current_user_avatar(
        file: UploadFile,
        current_user: Annotated[User, Depends(get_current_user)],
        session: Annotated[Session, Depends(get_session)]
):
    filename = 'user/' + current_user.id.__str__()

    s3_client.upload_fileobj(Fileobj=file.file,
                             Bucket=bucket_name,
                             Key=filename,
                             ExtraArgs={'ContentType': file.content_type}
                             )
    current_user.avatar = cloudfront_url + filename
    return save_data_to_db(session, current_user, dto=UserResponse)


@user_router.post('/instructor', response_model=UserResponse)
async def become_instructor(
        current_user: Annotated[User, Depends(get_current_user)],
        session: Annotated[Session, Depends(get_session)]
):
    current_user.is_instructor = True
    return save_data_to_db(session, current_user, dto=UserResponse)
