from typing import Annotated

from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from auth.auth_user import get_current_user
from courses.models import Course, CourseResponse, CourseCreate
from data.engine import engine

courses_router = APIRouter(
    prefix="/course",
    tags=["course"],
)


@courses_router.get("/", response_model=list[CourseResponse])
async def get_courses():
    with Session(engine) as session:
        query = select(Course)
        courses = session.exec(query).all()
        return courses


@courses_router.post("/", response_model=CourseResponse)
async def create_course(course: CourseCreate):
    with Session(engine) as session:
        session.add(course)
        session.commit()
        session.refresh(course)
        return course
