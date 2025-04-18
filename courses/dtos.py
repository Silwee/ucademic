import json
import uuid
from datetime import datetime
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


class LessonResourceDto(DtoModel):
    title: str
    url: str


class LessonCreate(DtoModel):
    title: str
    type: Literal["video", "text", "file"] | None = 'video'
    free_preview: bool | None = False
    text: dict | str | None = None

    @field_validator("text")
    def validate_text(cls, v):
        """Dump the description as a string in database"""
        if v is None:
            return v
        if isinstance(v, dict):
            return json.dumps(v)
        raise TypeError("Text must be in JSON")


class LessonResponse(DtoModel):
    id: uuid.UUID
    title: str
    duration: int | None = None
    free_preview: bool
    link: str | None = None
    text: dict | str | None = None

    resources: list[LessonResourceDto] | None = None

    @field_validator("text")
    def validate_description(cls, v):
        """Load the text back to JSON (as a dict) if not null"""
        if v is not None:
            return json.loads(v)
        return v


class SectionCreate(DtoModel):
    sectionTitle: str


class SectionResponse(DtoModel):
    id: uuid.UUID
    sectionTitle: str
    lessons: list[LessonResponse] | None = None


class CourseCreate(DtoModel):
    title: str
    headline: str | None = None
    description: dict | str | None = None
    categories: list[str] | list[Category]
    level: Literal["beginner", "intermediate", "advanced"]
    language: Literal["vi", "en"]
    price: Decimal = Field(ge=0, description="Price must be greater than 0")

    requirements: list[str] | str | None = None
    what_you_will_learn: list[str] | str | None = None

    @field_validator("description")
    def validate_description(cls, v):
        """Dump the description as a string in database"""
        if v is None:
            return v
        if isinstance(v, dict):
            return json.dumps(v)
        raise TypeError("Description must be in JSON")

    @field_validator("requirements")
    def validate_requirements(cls, v):
        """Dump the requirements as a string in database"""
        if v is None:
            return v
        if isinstance(v, list):
            return "`".join(v)
        raise TypeError("Requirements must be a List")

    @field_validator("what_you_will_learn")
    def validate_what_you_will_learn(cls, v):
        """Dump the what_you_will_learn as a string in database"""
        if v is None:
            return v
        if isinstance(v, list):
            return "`".join(v)
        raise TypeError("WhatYouWillLearn must be a List")


class CourseUpdate(DtoModel):
    title: str | None = None
    headline: str | None = None
    description: dict | str | None = None
    level: Literal["beginner", "intermediate", "advanced"] | None = None
    language: Literal["vi", "en"] | None = None
    price: Decimal | None = Field(default=0, ge=0, description="Price must be greater than 0")
    last_updated: datetime | None = datetime.now()

    requirements: str | None = None
    what_you_will_learn: list[str] | str | None = None
    categories: list[str] | list[Category] | None = None

    @field_validator("description", mode="before")
    def validate_description(cls, v):
        """Dump the description as a string in database"""
        if v is None:
            return v
        if isinstance(v, dict):
            return json.dumps(v)
        raise TypeError("Description must be in JSON")

    @field_validator("requirements")
    def validate_requirements(cls, v):
        """Dump the requirements as a string in database"""
        if v is None:
            return v
        if isinstance(v, list):
            return "`".join(v)
        raise TypeError("Requirements must be a List")

    @field_validator("what_you_will_learn")
    def validate_what_you_will_learn(cls, v):
        """Dump the what_you_will_learn as a string in database"""
        if v is None:
            return v
        if isinstance(v, list):
            return "`".join(v)
        raise TypeError("WhatYouWillLearn must be a List")


class CourseResponse(DtoModel):
    id: uuid.UUID
    title: str
    headline: str | None = None
    description: dict | str | None = None
    categories: list[str] | list[Category]
    level: str
    language: str
    price: float
    thumbnail: str | None = None

    requirements: list[str] | str | None = None
    what_you_will_learn: list[str] | str | None = None
    rating: float | None = None
    students: int | None = None
    duration: int | None = None
    lessons: int | None = None
    last_updated: datetime | None = None

    contents: list[SectionResponse] | None = None

    @field_validator("description")
    def validate_description(cls, v):
        """Load the description back to JSON (as a dict) if not null"""
        if v is not None:
            return json.loads(v)
        return v

    @field_validator("requirements")
    def validate_requirements(cls, v: str | None):
        """Load the requirements back to list if not null"""
        if v is not None:
            return v.split('`')
        return v

    @field_validator("what_you_will_learn")
    def validate_what_you_will_learn(cls, v: str | None):
        """Load the what_you_will_learn back to list if not null"""
        if v is not None:
            return v.split('`')
        return v

    @field_validator("categories")
    def validate_categories(cls, v: list[Category]):
        return [category.name for category in v]
