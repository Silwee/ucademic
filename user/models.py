import uuid

from sqlmodel import SQLModel, Field


class User(SQLModel, table=True):
    id: uuid.UUID = Field(primary_key=True, index=True, default_factory=uuid.uuid4)
    email: str = Field(unique=True, index=True)
    hashed_password: str = Field(min_length=8)
    full_name: str | None = Field(default=None, index=True)
    phone_number: str | None = Field(default=None, index=True)
    date_of_birth: str | None = Field(default=None, index=True)
    gender: str | None = Field(default=None, index=True)
    bio: str | None = Field(default=None, index=True)
    avatar: bytes | None = Field(default=None, index=True)
    avatar_content_type: str | None = Field(default=None, index=True)


class UserCreate(SQLModel):
    email: str
    password: str


class UserUpdateProfile(SQLModel):
    full_name: str | None = None
    phone_number: str | None = None
    date_of_birth: str | None
    gender: str | None
    bio: str | None


class UserResponse(SQLModel):
    id: uuid.UUID
    email: str
    full_name: str | None = None
    phone_number: str | None = None
    date_of_birth: str | None
    gender: str | None
    bio: str | None


class UserAvatarResponse(SQLModel):
    avatar: bytes | None





