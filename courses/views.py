from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, UploadFile, HTTPException, status
from fastapi_pagination import Page, paginate
from sqlmodel import select, col, Session

from auth.auth_user import get_current_user
from courses.dtos import CourseResponse, CourseCreate, CategoryResponse, CategoryCreate, CourseUpdate
from courses.models import Course, Category
from data.aws import s3_client, bucket_name, cloudfront_url
from data.engine import engine
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
async def create_course(course_create: CourseCreate):
    query = select(Course).where(col(Course.title) == course_create.title)
    courses = run_sql_select_query(query, mode="all")

    if len(courses) != 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Course name already existed."
        )

    # Find corresponding Category from category name
    query = select(Category).where(col(Category.name).in_(course_create.categories))
    categories = run_sql_select_query(query, mode="all")

    if len(categories) == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found."
        )

    db_course = Course.model_validate(course_create, update={"categories": categories})
    return run_sql_save_query(db_course, dto=CourseResponse)


# @courses_router.put(path="/{course_id}",
#                     responses={
#                         200: {"model": CourseResponse},
#                         404: {"description": "Course/Category not found."},
#                     }
#                     )
# async def update_course(course_id: UUID, course_update: CourseUpdate):
#     query = select(Course).where(col(Course.id) == course_id)
#     course = run_sql_select_query(query, mode="one")
#
#     if course is None:
#         raise HTTPException(
#             status_code=status.HTTP_409_CONFLICT,
#             detail="Course not found."
#         )
#
#     query = select(Category).where(col(Category.name).in_(course_update.categories))
#     categories = run_sql_select_query(query, mode="all")
#     if len(categories) == 0 and course_update.categories is not None:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Category not found."
#         )
#
#
#         course.categories.clear()
#         for category in categories:
#             course.categories.add(category)
#         session.add(course)
#         session.commit()
#         session.refresh(course)
#
#     course.sqlmodel_update(course_update.model_dump(exclude_unset=True))
#     return run_sql_save_query(course, dto=CourseResponse, old=True)


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
async def create_category(category_create: CategoryCreate):
    query = select(Category).where(col(Category.name) == category_create.name)
    existed_category = run_sql_select_query(query, mode="all")

    if len(existed_category) != 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Category name already existed."
        )

    category = Category.model_validate(category_create)
    return run_sql_save_query(category)
