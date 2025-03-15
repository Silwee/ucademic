import uuid
from decimal import Decimal

from pydantic import field_validator
from sqlmodel import SQLModel, Field


class Course(SQLModel, table=True):
    id: uuid.UUID = Field(primary_key=True, index=True, default_factory=uuid.uuid4)
    title: str = Field(max_length=100)
    description: str | None = Field(max_length=100)
    category: str = Field(max_length=100)
    level: str = Field(max_length=15)
    language: str = Field(max_length=10)
    price: Decimal = Field(decimal_places=2)


class CourseCreate(SQLModel):
    title: str
    description: str | None
    category: str
    level: str
    language: str
    price: float

    @field_validator("level", mode="before")
    def validate_level(cls, v):
        if v not in ["Beginner", "Intermediate", "Advanced", "beginner", "intermediate", "advanced"]:
            raise ValueError("Invalid level")
        return v

    @field_validator("language", mode="before")
    def validate_language(cls, v):
        if v not in ["Vietnamese", "English", "vietnamese", "english", "vi", "en"]:
            raise ValueError("Invalid language")
        return v

    @field_validator("price", mode="before")
    def validate_price(cls, v):
        if v is not float:
            raise ValueError("Invalid price")
        if v < 0:
            raise ValueError("Price must be greater than 0")
        return v


class CourseResponse(SQLModel):
    id: uuid.UUID
    title: str
    description: str | None
    category: str
    level: str
    language: str
    price: float
