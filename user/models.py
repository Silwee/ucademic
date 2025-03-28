import uuid

from sqlmodel import SQLModel, Field

from data.utils import new_uuid


class User(SQLModel, table=True):
    id: uuid.UUID = Field(primary_key=True, index=True, default_factory=new_uuid)
    email: str = Field(unique=True, index=True)
    hashed_password: str = Field(min_length=8)
    full_name: str | None = Field(default=None, index=True)
    phone_number: str | None = Field(default=None, index=True)
    date_of_birth: str | None = Field(default=None, index=True)
    gender: str | None = Field(default=None, index=True)
    bio: str | None = Field(default=None)
    avatar: str | None = Field(default=None)
