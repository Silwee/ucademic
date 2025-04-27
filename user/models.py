import uuid
from typing import TYPE_CHECKING

from sqlmodel import SQLModel, Field, Relationship

from data.utils import new_uuid

if TYPE_CHECKING:
    from courses.models import Course


class UserCourseLink(SQLModel, table=True):
    course_id: uuid.UUID = Field(default=None, primary_key=True, index=True, foreign_key="course.id")
    user_id: uuid.UUID = Field(default=None, primary_key=True, index=True, foreign_key="user.id")


class User(SQLModel, table=True):
    id: uuid.UUID = Field(primary_key=True, index=True, default_factory=new_uuid)
    email: str = Field(unique=True, index=True)
    hashed_password: str = Field(min_length=8)
    full_name: str | None = Field(default=None, index=True)
    phone_number: str | None = Field(default=None, index=True)
    date_of_birth: str | None = Field(default=None, index=True)
    gender: str | None = Field(default=None, index=True)
    bio: str | None = Field(default=None)
    avatar: str | None = Field(default=None)

    is_instructor: bool | None = Field(default=None, index=True)
    taught_courses: list["Course"] = Relationship(back_populates="instructor")

    learned_courses: list["Course"] = Relationship(back_populates="students", link_model=UserCourseLink)
