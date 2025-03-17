import uuid
from datetime import date

from pydantic import field_validator
from sqlmodel import SQLModel, Field

from data.core import DtoModel


class User(SQLModel, table=True):
    id: uuid.UUID = Field(primary_key=True, index=True, default_factory=uuid.uuid4)
    email: str = Field(unique=True, index=True)
    hashed_password: str = Field(min_length=8)
    full_name: str | None = Field(default=None, index=True)
    phone_number: str | None = Field(default=None, index=True)
    date_of_birth: str | None = Field(default=None, index=True)
    gender: str | None = Field(default=None, index=True)
    bio: str | None = Field(default=None)
    avatar: bytes | None = Field(default=None)
    avatar_content_type: str | None = Field(default=None)


class UserCreate(DtoModel):
    email: str
    password: str
    # TODO: validate email and password


class UserUpdateProfile(DtoModel):
    full_name: str
    phone_number: str
    date_of_birth: date | str
    gender: str
    bio: str | None = None

    @field_validator("date_of_birth")
    def date_of_birth_validator(cls, v):
        if isinstance(v, str):
            if date.fromisoformat(v) > date.today():
                raise ValueError("Date of birth must be in the past")
        if isinstance(v, date):
            if v > date.today():
                raise ValueError("Date of birth must be in the past")
        return v.__str__()

    @field_validator("phone_number")
    def phone_number_validator(cls, v):
        if not v.isdigit() or len(v) < 10 or len(v) > 15:
            raise ValueError("Phone number must be between 10 and 15 digits")
        return v

    @field_validator("gender")
    def gender_validator(cls, v):
        if v not in ["Male", "Female"]:
            raise ValueError("Gender must be Male or Female")
        return v


class UserResponse(DtoModel):
    id: uuid.UUID
    email: str
    full_name: str | None = None
    phone_number: str | None = None
    date_of_birth: date | None = None
    gender: str | None = None
    bio: str | None = None

    @field_validator("date_of_birth", mode="before")
    def date_of_birth_validator(cls, v):
        if v is not None and isinstance(v, str):
            return date.fromisoformat(v)
        return v
