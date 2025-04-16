import uuid
from datetime import datetime
from decimal import Decimal

from sqlmodel import SQLModel, Field, Relationship

from data.utils import new_uuid


class CourseCategoryLink(SQLModel, table=True):
    course_id: uuid.UUID = Field(default=None, primary_key=True, index=True, foreign_key="course.id")
    category_id: uuid.UUID = Field(default=None, primary_key=True, index=True, foreign_key="category.id")


class Course(SQLModel, table=True):
    id: uuid.UUID = Field(primary_key=True, index=True, default_factory=new_uuid)
    title: str = Field(max_length=100, index=True)
    headline: str | None = Field(default=None, nullable=True)
    description: str | None = Field(default=None, nullable=True)
    level: str = Field(max_length=15, index=True)
    language: str = Field(max_length=10, index=True)
    price: Decimal = Field(decimal_places=2, index=True)
    thumbnail: str | None = Field(default=None, nullable=True)

    requirements: str | None = Field(default=None, nullable=True)
    what_will_you_learn: str | None = Field(default=None, nullable=True)
    rating: float | None = Field(default=4.5, nullable=True, index=True)
    students: int | None = Field(default=20000, nullable=True, index=True)
    duration: int | None = Field(default=140, nullable=True, index=True)
    lessons: int | None = Field(default=0, nullable=True, index=True)
    last_updated: datetime | None = Field(default_factory=datetime.now, nullable=True, index=True)

    contents: list["Section"] = Relationship(back_populates="course_section")
    categories: list["Category"] = Relationship(back_populates="courses", link_model=CourseCategoryLink)


class Category(SQLModel, table=True):
    id: uuid.UUID = Field(primary_key=True, index=True, default_factory=new_uuid)
    name: str

    courses: list["Course"] = Relationship(back_populates="categories", link_model=CourseCategoryLink)


class Section(SQLModel, table=True):
    id: uuid.UUID = Field(primary_key=True, index=True, default_factory=new_uuid)
    sectionTitle: str = Field(index=True)

    course_id: uuid.UUID | None = Field(default=None, index=True, foreign_key="course.id")
    course_section: Course | None = Relationship(back_populates="contents")

    lessons: list["Lesson"] = Relationship(back_populates="section_lesson")


class Lesson(SQLModel, table=True):
    id: uuid.UUID = Field(primary_key=True, index=True, default_factory=new_uuid)
    title: str = Field(index=True)

    duration: int | None = Field(default=None, nullable=True, index=True)
    free_preview: bool = Field(default=False, index=True)
    link: str | None = Field(default=None, nullable=True)

    section_id: uuid.UUID | None = Field(default=None, index=True, foreign_key="section.id")
    section_lesson: Section | None = Relationship(back_populates="lessons")


# class VideoLesson(Lesson, table=True):

