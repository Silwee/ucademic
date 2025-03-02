import uuid

from sqlmodel import SQLModel, Field


class User(SQLModel, table=True):
    id: uuid.UUID = Field(primary_key=True, index=True, default_factory=uuid.uuid4)
    email: str = Field(unique=True, index=True)
    hashed_password: str = Field(min_length=8)
    full_name: str | None = Field(default=None, index=True)


class UserCreate(SQLModel):
    email: str
    password: str


class UserResponse(SQLModel):
    id: uuid.UUID
    email: str
    full_name: str | None = None





