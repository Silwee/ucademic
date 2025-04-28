import json
import uuid
from datetime import date
from typing import Literal

from pydantic import field_validator, Field
from data.utils import DtoModel


class UserCreate(DtoModel):
    email: str
    password: str
    # TODO: validate email and password


class UserUpdateProfile(DtoModel):
    full_name: str
    phone_number: str = Field(pattern=r'^\d*$', min_length=10, max_length=15,
                              description="Phone number must be between 10 and 15 digits")
    date_of_birth: date | str
    gender: Literal['Male', "Female"] = Field()
    bio: dict | str | None = None

    @field_validator("date_of_birth")
    def date_of_birth_validator(cls, v):
        if isinstance(v, str):
            if date.fromisoformat(v) > date.today():
                raise ValueError("Date of birth must be in the past")
        if isinstance(v, date):
            if v > date.today():
                raise ValueError("Date of birth must be in the past")
        return v.__str__()

    @field_validator("bio")
    def validate_bio(cls, v):
        """Dump the bio as a string in database"""
        if v is None:
            return v
        if isinstance(v, dict):
            return json.dumps(v)
        raise TypeError("Bio must be in JSON")


class UserResponse(DtoModel):
    id: uuid.UUID
    email: str
    full_name: str | None = None
    phone_number: str | None = None
    date_of_birth: date | None = None
    gender: str | None = None
    bio: dict | str | None = None
    avatar: str | None = None

    is_instructor: bool | None = None

    @field_validator("date_of_birth", mode="before")
    def date_of_birth_validator(cls, v):
        if v is not None and isinstance(v, str):
            return date.fromisoformat(v)
        return v

    @field_validator("bio")
    def validate_bio(cls, v):
        """Load the bio back to JSON (as a dict) if not null"""
        if v is not None:
            return json.loads(v)
        return v
