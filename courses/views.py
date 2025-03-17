from typing import Annotated

from fastapi import APIRouter, Depends
from sqlmodel import Session, select, col

from auth.auth_user import get_current_user
from courses.models import Course, CourseResponse, CourseCreate, Category, CategoryResponse, CategoryCreate
from data.engine import engine

courses_router = APIRouter(
    prefix="/course",
    tags=["course"],
)


@courses_router.get("/all", response_model=list[CourseResponse])
async def get_all_courses():
    with Session(engine) as session:
        query = select(Course)
        courses = session.exec(query).all()
        # Have to do this for many-to-many relationship
        return [CourseResponse.model_validate(course) for course in courses]


@courses_router.get("/{course_id}", response_model=CourseResponse)
async def get_course(course_id: int):
    with Session(engine) as session:
        query = select(Course).where(col(Course.id) == course_id)
        course = session.exec(query).first()
        # Have to do this for many-to-many relationship
        return CourseResponse.model_validate(course)


@courses_router.post("/", response_model=CourseResponse)
async def create_course(course: CourseCreate):
    with Session(engine) as session:
        # Find corresponding Category from category name
        query = select(Category).where(col(Category.name).in_(course.categories))
        categories = session.exec(query).all()

        db_course = Course.model_validate(course, update={"categories": categories, "language": course.languages})

        session.add(db_course)
        session.commit()
        session.refresh(db_course)
        # Have to do this for many-to-many relationship
        return CourseResponse.model_validate(db_course)


@courses_router.get("/category/all", response_model=list[CategoryResponse])
async def get_course():
    with Session(engine) as session:
        query = select(Category)
        category = session.exec(query).all()
        return category


@courses_router.post("/category", response_model=CategoryResponse)
async def create_category(category: CategoryCreate):
    with Session(engine) as session:
        db_category = Category.model_validate(category)
        session.add(db_category)
        session.commit()
        session.refresh(db_category)
        return db_category
