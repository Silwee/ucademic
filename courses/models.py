import uuid
from decimal import Decimal

from pydantic import field_validator
from sqlmodel import SQLModel, Field

from data.core import DtoModel


class Course(SQLModel, table=True):
    id: uuid.UUID = Field(primary_key=True, index=True, default_factory=uuid.uuid4)
    title: str = Field(max_length=100)
    description: str | None = Field(max_length=100)
    category: str = Field(max_length=100)
    level: str = Field(max_length=15)
    language: str = Field(max_length=10)
    price: Decimal = Field(decimal_places=2)


class CourseCreate(DtoModel):
    title: str
    description: str | None = None
    category: str
    level: str
    language: str
    price: Decimal

    @field_validator("level")
    def validate_level(cls, v):
        if v not in ["Beginner", "Intermediate", "Advanced"]:
            raise ValueError("Level must be Beginner, Intermediate or Advanced")
        return v

    @field_validator("language")
    def validate_language(cls, v):
        if v not in ["Vietnamese", "English", "vi", "en"]:
            raise ValueError("Language must be Vietnamese or English (vi, en)")
        return v

    @field_validator("price")
    def validate_price(cls, v):
        if v < 0:
            raise ValueError("Price must be greater than 0")
        return v


class CourseResponse(DtoModel):
    id: uuid.UUID
    title: str
    description: str | None = None
    category: str
    level: str
    language: str
    price: float
