import uuid
from decimal import Decimal

from pydantic import field_validator, Json
from pydantic_core import to_json
from sqlmodel import SQLModel, Field, Relationship

from data.core import DtoModel


class CourseCategoryLink(SQLModel, table=True):
    course_id: uuid.UUID = Field(default=None, primary_key=True, index=True, foreign_key="course.id")
    category_id: uuid.UUID = Field(default=None, primary_key=True, index=True, foreign_key="category.id")


class Course(SQLModel, table=True):
    id: uuid.UUID = Field(primary_key=True, index=True, default_factory=uuid.uuid4)
    title: str = Field(max_length=100, index=True)
    description: str | None = Field
    level: str = Field(max_length=15, index=True)
    language: str = Field(max_length=10, index=True)
    price: Decimal = Field(decimal_places=2, index=True)

    categories: list["Category"] = Relationship(back_populates="courses", link_model=CourseCategoryLink)


class Category(SQLModel, table=True):
    id: uuid.UUID = Field(primary_key=True, index=True, default_factory=uuid.uuid4)
    name: str

    courses: list["Course"] = Relationship(back_populates="categories", link_model=CourseCategoryLink)


class CourseCreate(DtoModel):
    title: str
    description: dict | None = None
    category: list[str] | list[Category]
    level: str
    language: str
    price: Decimal

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "title": "string",
                    "description": {
                        "title": "string"
                    },
                    "category": [
                        "Development"
                    ],
                    "level": "Beginner",
                    "language": "Vietnamese",
                    "price": 0
                }
            ]
        }
    }

    @field_validator("level")
    def validate_level(cls, v: str):
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

    @field_validator("description")
    def validate_description(cls, v: dict | None = None):
        if v is not None:
            return v.__str__()
        return v


class CategoryCreate(DtoModel):
    name: str


class CategoryResponse(DtoModel):
    id: uuid.UUID
    name: str


class CourseResponse(DtoModel):
    id: uuid.UUID
    title: str
    description: str | Json | None = None
    categories: list[CategoryResponse] | list[Category]
    level: str
    language: str
    price: float

    @field_validator("description")
    def validate_description(cls, v):
        if v is not None:
            return to_json(v)
        return v

    @field_validator("categories")
    def validate_categories(cls, v: list[Category]):
        categories = []
        for category in v:
            categories.append(CategoryResponse.model_validate(category.model_dump()))
        return categories
