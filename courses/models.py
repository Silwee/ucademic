import json
import uuid
from decimal import Decimal

from pydantic import field_validator
from sqlmodel import SQLModel, Field, Relationship

from data.core import DtoModel, new_uuid


class CourseCategoryLink(SQLModel, table=True):
    course_id: uuid.UUID = Field(default=None, primary_key=True, index=True, foreign_key="course.id")
    category_id: uuid.UUID = Field(default=None, primary_key=True, index=True, foreign_key="category.id")


class Course(SQLModel, table=True):
    id: uuid.UUID = Field(primary_key=True, index=True, default_factory=new_uuid)
    title: str = Field(max_length=100, index=True)
    description: str | None = Field
    level: str = Field(max_length=15, index=True)
    languages: str = Field(max_length=15, index=True)
    price: Decimal = Field(decimal_places=2, index=True)

    categories: list["Category"] = Relationship(back_populates="courses", link_model=CourseCategoryLink)


class Category(SQLModel, table=True):
    id: uuid.UUID = Field(primary_key=True, index=True, default_factory=new_uuid)
    name: str

    courses: list["Course"] = Relationship(back_populates="categories", link_model=CourseCategoryLink)


class CourseCreate(DtoModel):
    title: str
    description: dict | str | None = None
    categories: list[str] | list[Category]
    level: str
    languages: list[str] | str
    price: Decimal

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "title": "string",
                    "description": {
                        "block": "string"
                    },
                    "categories": [
                        "Development"
                    ],
                    "level": "beginner",
                    "languages": [
                        "vi"
                    ],
                    "price": 0
                }
            ]
        }
    }

    @field_validator("level")
    def validate_level(cls, v: str):
        if v not in ["beginner", "intermediate", "advanced"]:
            raise ValueError("Level must be Beginner, Intermediate or Advanced")
        return v

    @field_validator("languages")
    def validate_languages(cls, v: list[str]) -> str:
        r = ""
        for language in v:
            if language not in ["vi", "en"]:
                raise ValueError("Language must be Vietnamese or English (vi, en)")
            r += language + '+'
        return r[:-1]

    @field_validator("price")
    def validate_price(cls, v):
        if v < 0:
            raise ValueError("Price must be greater than 0")
        return v

    @field_validator("description")
    def validate_description(cls, v):
        if v is not None:
            return json.dumps(v)
        return v


class CategoryCreate(DtoModel):
    name: str


class CategoryResponse(DtoModel):
    id: uuid.UUID
    name: str


class CourseResponse(DtoModel):
    id: uuid.UUID
    title: str
    description: dict | str | None = None
    categories: list[str] | list[Category]
    level: str
    languages:  list[str] | str
    price: float

    @field_validator("description")
    def validate_description(cls, v: str):
        if v is not None:
            return json.loads(v)
        return v

    @field_validator("categories")
    def validate_categories(cls, v: list[Category]):
        return [category.name for category in v]

    @field_validator("languages")
    def validate_languages(cls, v: str) -> list[str]:
        return v.split(sep='+')

