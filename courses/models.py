import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlmodel import SQLModel, Field, Relationship

from data.utils import new_uuid
from user.models import UserCourseLink

if TYPE_CHECKING:
    from user.models import User


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
    what_you_will_learn: str | None = Field(default=None, nullable=True)
    rating: float | None = Field(default=0, nullable=True, index=True)
    last_updated: datetime | None = Field(default_factory=datetime.now, nullable=True, index=True)

    contents: list["Section"] = Relationship(back_populates="course_section")
    categories: list["Category"] = Relationship(back_populates="courses", link_model=CourseCategoryLink)

    instructor_id: uuid.UUID = Field(default=None, index=True, foreign_key="user.id")
    instructor: "User" = Relationship(back_populates="taught_courses")

    students: list["User"] = Relationship(back_populates="learned_courses", link_model=UserCourseLink)


class Category(SQLModel, table=True):
    id: uuid.UUID = Field(primary_key=True, index=True, default_factory=new_uuid)
    name: str

    courses: list["Course"] = Relationship(back_populates="categories", link_model=CourseCategoryLink)


class Section(SQLModel, table=True):
    id: uuid.UUID = Field(primary_key=True, index=True, default_factory=new_uuid)
    section_title: str = Field(index=True, nullable=True)

    course_id: uuid.UUID | None = Field(default=None, index=True, foreign_key="course.id")
    course_section: Course | None = Relationship(back_populates="contents")

    lessons: list["Lesson"] = Relationship(back_populates="section_lesson")
    quizzes: list["Quiz"] = Relationship(back_populates="section_quiz")


class Lesson(SQLModel, table=True):
    id: uuid.UUID = Field(primary_key=True, index=True, default_factory=new_uuid)
    title: str = Field(index=True)
    type: str = Field(default='video', index=True)
    order_in_section: int = Field(default=None, nullable=True, index=True)

    # For video type
    duration: int | None = Field(default=None, nullable=True, index=True)
    free_preview: bool = Field(default=False, index=True)

    # For text type
    text: str | None = Field(default=None, nullable=True)

    # For video/file type
    link: str | None = Field(default=None, nullable=True)

    section_id: uuid.UUID | None = Field(default=None, index=True, foreign_key="section.id")
    section_lesson: Section | None = Relationship(back_populates="lessons")
    resources: list["LessonResource"] = Relationship(back_populates="lesson_resource")


class Quiz(SQLModel, table=True):
    id: uuid.UUID = Field(primary_key=True, index=True, default_factory=new_uuid)
    title: str = Field(index=True)
    order_in_section: int = Field(default=None, nullable=True, index=True)

    section_id: uuid.UUID | None = Field(default=None, index=True, foreign_key="section.id")
    section_quiz: Section | None = Relationship(back_populates="quizzes")
    questions: list["QuizQuestion"] = Relationship(back_populates="quiz_question")


class QuizQuestion(SQLModel, table=True):
    id: uuid.UUID = Field(primary_key=True, index=True, default_factory=new_uuid)
    question_name: str = Field(index=True, nullable=False)
    type: str = Field(default='single', index=True, nullable=True)
    options: str = Field(default=None, nullable=True)
    correct_answer: str = Field(default=None, nullable=True)

    quiz_id: uuid.UUID | None = Field(default=None, nullable=True, index=True, foreign_key="quiz.id")
    quiz_question: Quiz | None = Relationship(back_populates="questions")


class LessonResource(SQLModel, table=True):
    title: str = Field(primary_key=True, index=True, nullable=False)
    url: str | None = Field(default=None, nullable=True)

    lesson_id: uuid.UUID | None = Field(default=None, index=True, foreign_key="lesson.id")
    lesson_resource: Lesson | None = Relationship(back_populates="resources")
