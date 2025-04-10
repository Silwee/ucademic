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

courses_router = APIRouter(
    prefix="/course",
    tags=["course"],
)


@courses_router.get("/all")
async def get_all_courses() -> Page[CourseResponse]:
    with Session(engine) as session:
        courses = session.exec(select(Course)).all()
        return paginate([CourseResponse.model_validate(course) for course in courses])


@courses_router.get("/{course_id}", response_model=CourseResponse)
async def get_course(course_id: UUID):
    with Session(engine) as session:
        course = session.exec(select(Course).where(col(Course.id) == course_id)).first()
        return CourseResponse.model_validate(course)


@courses_router.post(path="/{course_id}/thumbnail",
                     responses={
                         200: {"model": CourseResponse},
                         404: {"description": "Course not found"},
                     }
                     )
async def upload_course_thumbnail(course_id: UUID, file: UploadFile):
    with Session(engine) as session:
        course = session.exec(select(Course).where(col(Course.id) == course_id)).first()
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
        session.add(course)
        session.commit()
        session.refresh(course)
        return course


@courses_router.post(path="/",
                     responses={
                         200: {"model": CourseResponse},
                         404: {"description": "Category not found."},
                         409: {"description": "Course title already existed."},
                     }
                     )
async def create_course(course_create: CourseCreate):
    with Session(engine) as session:
        courses = session.exec(select(Course)
                               .where(col(Course.title) == course_create.title)
                               ).all()
        if len(courses) != 0:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Course name already existed."
            )

        categories = session.exec(select(Category)
                                  .where(col(Category.name).in_(course_create.categories))
                                  ).all()
        if len(categories) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found."
            )

        course = Course.model_validate(course_create, update={"categories": categories})
        session.add(course)
        session.commit()
        session.refresh(course)
        return course


@courses_router.put(path="/{course_id}",
                    responses={
                        200: {"model": CourseResponse},
                        404: {"description": "Course/Category not found."},
                    }
                    )
async def update_course(course_id: UUID, course_update: CourseUpdate):
    with Session(engine) as session:
        course = session.exec(select(Course)
                              .where(col(Course.id) == course_id)
                              ).first()

        if course is None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Course not found."
            )

        categories = session.exec(select(Category)
                                  .where(col(Category.name).in_(course_update.categories))
                                  ).all()
        if len(categories) == 0 and course_update.categories is not None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found."
            )

        course.sqlmodel_update(course_update.model_dump(exclude_unset=True))
        course.categories = categories
        session.add(course)
        session.commit()
        session.refresh(course)

        return course


@courses_router.get("/category/all", response_model=list[CategoryResponse])
async def get_all_category():
    with Session(engine) as session:
        return session.exec(select(Category)).all()


@courses_router.post(path="/category",
                     responses={
                         200: {"model": CategoryResponse},
                         409: {"description": "Category already existed."},
                     }
                     )
async def create_category(category_create: CategoryCreate):
    with (Session(engine) as session):
        existed_category = session.exec(select(Category)
                                        .where(col(Category.name) == category_create.name)
                                        ).all()
        if len(existed_category) != 0:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Category name already existed."
            )

        category = Category.model_validate(category_create)
        session.add(category)
        session.commit()
        session.refresh(category)
        return category
