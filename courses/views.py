from typing import Annotated
from uuid import UUID

import av
from fastapi import APIRouter, Depends, UploadFile, HTTPException, status, BackgroundTasks
from fastapi_pagination import Page, paginate
from sqlmodel import select, col, Session

from auth.auth_user import get_current_user
from courses.dtos import CourseResponse, CourseCreate, CategoryResponse, CategoryCreate, CourseUpdate, SectionCreate, \
    LessonCreate, LessonResponse, SectionResponse, LessonResourceDto
from courses.models import Course, Category, Section, Lesson, LessonResource
from courses.service import get_lesson, transcode_video, lesson_uploading
from data.aws import s3_client, bucket_name, cloudfront_url, media_convert_client
from data.engine import engine, get_session

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

        filename = 'course/thumbnail/' + course.id.__str__()

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


@courses_router.get("/section/{section_id}", response_model=SectionResponse)
async def get_section(section_id: UUID):
    with Session(engine) as session:
        section = session.get(Section, section_id)
        return SectionResponse.model_validate(section)


@courses_router.post("/{course_id}/section",
                     responses={
                         200: {"model": SectionResponse},
                         404: {"description": "Course not found."},
                     }
                     )
async def add_section(course_id: UUID, section_create: SectionCreate):
    with Session(engine) as session:
        course = session.exec(select(Course)
                              .where(col(Course.id) == course_id)
                              ).first()

        if course is None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Course not found."
            )

        section = Section.model_validate(section_create, update={"course_section": course})
        session.add(section)
        session.commit()
        session.refresh(section)
        return section


@courses_router.get("/lesson/{lesson_id}", response_model=LessonResponse)
async def get_lesson(lesson_id: UUID):
    with Session(engine) as session:
        lesson = session.get(Lesson, lesson_id)
        return LessonResponse.model_validate(lesson)


@courses_router.post("/section/{section_id}/lesson",
                     responses={
                         200: {"model": LessonResponse},
                         404: {"description": "Course/Section not found."},
                     }
                     )
async def add_lesson(section_id: UUID, lesson_create: LessonCreate):
    with Session(engine) as session:
        section = session.exec(select(Section)
                               .where(col(Section.id) == section_id)
                               ).first()

        if section is None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Course not found."
            )

        if lesson_create.type != 'text':
            lesson_create.text = None

        lesson = Lesson.model_validate(lesson_create, update={"section_lesson": section})
        session.add(lesson)
        session.commit()
        session.refresh(lesson)
        return lesson


@courses_router.post("/lesson/{lesson_id}/video",
                     responses={
                         200: {"model": LessonResponse},
                         404: {"description": "Lesson not found."},
                     }
                     )
async def upload_lesson_video(lesson_id: UUID,
                              file: UploadFile,
                              background_tasks: BackgroundTasks,
                              session: Annotated[Session, Depends(get_session)]):
    lesson = get_lesson(session, lesson_id)

    # Use PyAV to get the video's location
    duration_seconds = 0
    try:
        video_stream = av.open(file.file).streams.video[0]
        if video_stream.duration is not None and video_stream.time_base is not None:
            duration_seconds = int(video_stream.duration * video_stream.time_base)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can't determine video format."
        )

    path = 'course/video/' + lesson.id.__str__() + '/'

    # Reset file to start
    file.file.seek(0)

    # Upload the original video to s3
    s3_client.upload_fileobj(Fileobj=file.file,
                             Bucket=bucket_name,
                             Key=path + "original",
                             ExtraArgs={'ContentType': file.content_type}
                             )

    # Upload to s3 in the background
    background_tasks.add_task(transcode_video,
                              lesson_id=lesson.id,
                              path=path,
                              duration_seconds=duration_seconds)

    return lesson_uploading(session, lesson)


@courses_router.post("/lesson/{lesson_id}/resource", response_model=LessonResponse)
async def upload_lesson_resource(lesson_id: UUID, resource_create: LessonResourceDto):
    with Session(engine) as session:
        lesson = session.get(Lesson, lesson_id)
        if lesson is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lesson not found."
            )

        resource = LessonResource.model_validate(resource_create, update={"lesson_resource": lesson})
        session.add(resource)
        session.commit()
        session.refresh(resource)
        return LessonResponse.model_validate(resource.lesson_resource)


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
