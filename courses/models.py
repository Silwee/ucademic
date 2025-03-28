import uuid
from decimal import Decimal

from sqlmodel import SQLModel, Field, Relationship

from data.utils import new_uuid


class CourseCategoryLink(SQLModel, table=True):
    course_id: uuid.UUID = Field(default=None, primary_key=True, index=True, foreign_key="course.id")
    category_id: uuid.UUID = Field(default=None, primary_key=True, index=True, foreign_key="category.id")


class Course(SQLModel, table=True):
    id: uuid.UUID = Field(primary_key=True, index=True, default_factory=new_uuid)
    title: str = Field(max_length=100, index=True)
    description: str | None = Field
    level: str = Field(max_length=15, index=True)
    languages: str = Field(max_length=10, index=True)
    price: Decimal = Field(decimal_places=2, index=True)
    thumbnail: str | None = Field(default=None, nullable=True)

    categories: list["Category"] = Relationship(back_populates="courses", link_model=CourseCategoryLink)


class Category(SQLModel, table=True):
    id: uuid.UUID = Field(primary_key=True, index=True, default_factory=new_uuid)
    name: str

    courses: list["Course"] = Relationship(back_populates="categories", link_model=CourseCategoryLink)
