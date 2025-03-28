from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, UploadFile, HTTPException, status
from fastapi_pagination import Page, paginate
from sqlmodel import select, col

from auth.auth_user import get_current_user
from courses.dtos import CourseResponse, CourseCreate, CategoryResponse, CategoryCreate
from courses.models import Course, Category
from data.aws import s3_client, bucket_name, cloudfront_url
from data.query import run_sql_select_query, run_sql_save_query

courses_router = APIRouter(
    prefix="/course",
    tags=["course"],
)


@courses_router.get("/all")
async def get_all_courses() -> Page[CourseResponse]:
    query = select(Course)

    return paginate(run_sql_select_query(query, mode="all", dto=CourseResponse))


@courses_router.get("/{course_id}", response_model=CourseResponse)
async def get_course(course_id: UUID):
    query = select(Course).where(col(Course.id) == course_id)
    return run_sql_select_query(query, mode="one", dto=CourseResponse)


@courses_router.post(path="/{course_id}/thumbnail",
                     responses={
                         200: {"model": CourseResponse},
                         404: {"description": "Course not found"},
                     }
                     )
async def upload_course_thumbnail(course_id: UUID, file: UploadFile):
    query = select(Course).where(col(Course.id) == course_id)
    course = run_sql_select_query(query, mode="one")
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found",
        )

    filename = 'course/' + course.id.__str__()

    s3_client.upload_fileobj(Fileobj=file.file,
                             Bucket=bucket_name,
                             Key=filename,
                             ExtraArgs={'ContentType': file.content_type}
                             )
    course.thumbnail = cloudfront_url + filename
    return run_sql_save_query(course, dto=CourseResponse)



@courses_router.post(path="/",
                     responses={
                         200: {"model": CourseResponse},
                         404: {"description": "Category not found."},
                         409: {"description": "Course title already existed."},
                     }
                     )
async def create_course(course: CourseCreate):
    query = select(Course).where(col(Course.title) == course.title)
    courses = run_sql_select_query(query, mode="all")

    if len(courses) != 0:
        return HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Course name already existed."
        )

    # Find corresponding Category from category name
    query = select(Category).where(col(Category.name).in_(course.categories))
    categories = run_sql_select_query(query, mode="all")

    if len(categories) == 0:
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found."
        )

    db_course = Course.model_validate(course, update={"categories": categories})
    return run_sql_save_query(db_course, dto=CourseResponse)


@courses_router.get("/category/all", response_model=list[CategoryResponse])
async def get_all_category():
    query = select(Category)
    return run_sql_select_query(query, mode="all")


@courses_router.post(path="/category",
                     responses={
                         200: {"model": CategoryResponse},
                         409: {"description": "Category already existed."},
                     }
                     )
async def create_category(category: CategoryCreate):
    query = select(Category).where(col(Category.name) == category.name)
    courses = run_sql_select_query(query, mode="all")

    if len(courses) != 0:
        return HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Category name already existed."
        )

    db_category = Category.model_validate(category)
    return run_sql_save_query(db_category)
