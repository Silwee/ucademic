import json
import uuid
from decimal import Decimal
from typing import Literal

from pydantic import field_validator, Field

from courses.models import Category
from data.utils import DtoModel


class CategoryCreate(DtoModel):
    name: str


class CategoryResponse(DtoModel):
    id: uuid.UUID
    name: str


class CourseCreate(DtoModel):
    title: str
    description: dict | str | None = None
    categories: list[str] | list[Category]
    level: Literal["beginner", "intermediate", "advanced"]
    language: Literal["vi", "en"]
    price: Decimal = Field(ge=0, description="Price must be greater than 0")

    @field_validator("description", mode="before")
    def validate_description(cls, v):
        """Dump the description as a string in database"""
        if v is None:
            return v
        if isinstance(v, dict):
            return json.dumps(v)
        raise TypeError("Description must be in JSON")


class CourseUpdate(DtoModel):
    title: str | None = None
    description: dict | str | None = None
    categories: list[str] | list[Category] | None = None
    level: Literal["beginner", "intermediate", "advanced"] | None = None
    language: Literal["vi", "en"] | None = None
    price: Decimal | None = Field(default=0, ge=0, description="Price must be greater than 0")

    @field_validator("description", mode="before")
    def validate_description(cls, v):
        """Dump the description as a string in database"""
        if v is None:
            return v
        if isinstance(v, dict):
            return json.dumps(v)
        raise TypeError("Description must be in JSON")


class CourseResponse(DtoModel):
    id: uuid.UUID
    title: str
    description: dict | str | None = None
    categories: list[str] | list[Category]
    level: str
    language: str
    price: float
    thumbnail: str | None = None

    @field_validator("description")
    def validate_description(cls, v):
        """Load the description back to JSON (as a dict) if not null"""
        if v is not None:
            return json.loads(v)
        return v

    @field_validator("categories")
    def validate_categories(cls, v: list[Category]):
        return [category.name for category in v]
