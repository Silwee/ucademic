from typing import Annotated, Literal
from uuid import UUID

import av
from fastapi import APIRouter, Depends, UploadFile, HTTPException, status, BackgroundTasks
from fastapi_pagination import Page, paginate
from sqlmodel import select, col, Session

from auth.auth_user import get_current_user
from courses.dtos import CourseResponse, CourseCreate, CategoryResponse, CategoryCreate, CourseUpdate, SectionCreate, \
    LessonCreate, LessonResponse, SectionResponse, LessonResourceDto, QuizResponse, QuizCreate
from courses.models import Course, Category, Section, Lesson, LessonResource, Quiz, QuizQuestion
from courses.service import transcode_video
from data.aws import s3_client, bucket_name, cloudfront_url
from data.engine import engine, get_session
from data.service import get_data_in_db, save_data_to_db
from user.models import User

courses_router = APIRouter(
    prefix="/course",
    tags=["course"],
)


@courses_router.post("/{course_id}/register", response_model=CourseResponse)
async def register_course(
        course_id: UUID,
        current_user: Annotated[User, Depends(get_current_user)],
        session: Annotated[Session, Depends(get_session)]
):
    course = get_data_in_db(session, Course,
                            obj_id=course_id,
                            check_not_found=True)
    course.students.append(current_user)
    return save_data_to_db(session, course, dto=CourseResponse)


@courses_router.get("/all")
async def get_all_courses(
        session: Annotated[Session, Depends(get_session)]
) -> Page[CourseResponse]:
    return paginate(get_data_in_db(session, Course, mode='all', dto=CourseResponse))


@courses_router.get("/search")
async def search_courses(
        session: Annotated[Session, Depends(get_session)],
        keyword: str | None = None,
        level: Literal['beginner', 'intermediate', 'advanced'] | None = None,
        language: Literal['vi', 'en'] | None = None,
        price: Literal['paid', 'free'] | None = None,
        rating: float | None = None,
        duration: Literal['extraShort', 'short', 'medium', 'long', 'extraLong'] | None = None
) -> Page[CourseResponse]:
    query = select(Course)
    if keyword is not None:
        query = query.where(col(Course.title).contains(keyword))
    if level is not None:
        query = query.where(Course.level == level)
    if language is not None:
        query = query.where(Course.language == language)
    if rating is not None:
        query = query.where(Course.rating >= rating, Course.rating <= rating + 0.5)
    match price:
        case 'paid':
            query = query.where(Course.price > 0)
        case 'free':
            query = query.where(Course.price == 0)
    match duration:
        case 'extraShort':
            query = query.where(Course.duration >= 0, Course.duration < 1)
        case 'short':
            query = query.where(Course.duration >= 1, Course.duration < 3)
        case 'medium':
            query = query.where(Course.duration >= 3, Course.duration < 6)
        case 'long':
            query = query.where(Course.duration >= 6, Course.duration < 17)
        case 'extraLong':
            query = query.where(Course.duration >= 17)

    return paginate(get_data_in_db(session, Course,
                                   mode='query_all',
                                   query=query,
                                   dto=CourseResponse))


@courses_router.get("/my_courses", response_model=Page[CourseResponse])
async def get_my_courses(
        current_user: Annotated[User, Depends(get_current_user)],
        session: Annotated[Session, Depends(get_session)]
) -> Page[CourseResponse]:
    return paginate(get_data_in_db(session, Course,
                                   mode='query_all',
                                   query=select(Course).where(Course.instructor == current_user),
                                   dto=CourseResponse))


@courses_router.get("/attending_courses", response_model=Page[CourseResponse])
async def get_attending_courses(
        current_user: Annotated[User, Depends(get_current_user)],
        session: Annotated[Session, Depends(get_session)]
) -> Page[CourseResponse]:
    courses = get_data_in_db(session, Course,
                             mode='all',
                             dto=CourseResponse)
    c = []
    for course in courses:
        for student in course.students:
            if student.id == current_user.id:
                c.append(course)
    return paginate(c)


@courses_router.get("/{course_id}", response_model=CourseResponse)
async def get_course(
        course_id: UUID,
        session: Annotated[Session, Depends(get_session)]
):
    return get_data_in_db(session, Course,
                          obj_id=course_id,
                          dto=CourseResponse,
                          check_not_found=True)


@courses_router.post(path="/{course_id}/thumbnail",
                     responses={
                         200: {"model": CourseResponse},
                         404: {"description": "Course not found"},
                     }
                     )
async def upload_course_thumbnail(
        course_id: UUID,
        file: UploadFile,
        current_user: Annotated[User, Depends(get_current_user)],
        session: Annotated[Session, Depends(get_session)]
):
    course = get_data_in_db(session, Course, obj_id=course_id, check_not_found=True)

    if current_user.id != course.instructor_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to upload course",
        )

    filename = 'course/thumbnail/' + course.id.__str__()

    s3_client.upload_fileobj(Fileobj=file.file,
                             Bucket=bucket_name,
                             Key=filename,
                             ExtraArgs={'ContentType': file.content_type}
                             )
    course.thumbnail = cloudfront_url + filename
    return save_data_to_db(session, course, dto=CourseResponse)


@courses_router.post(path="/",
                     responses={
                         200: {"model": CourseResponse},
                         404: {"description": "Category not found."},
                         409: {"description": "Course title already existed."},
                     }
                     )
async def create_course(
        course_create: CourseCreate,
        current_user: Annotated[User, Depends(get_current_user)],
        session: Annotated[Session, Depends(get_session)]
):
    if not current_user.is_instructor:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to create course",
        )

    get_data_in_db(session, Course,
                   mode='query_one',
                   query=select(Course).where(col(Course.title) == course_create.title),
                   check_existed=True
                   )

    categories = get_data_in_db(session, Category,
                                mode='query_all',
                                query=select(Category)
                                .where(col(Category.name).in_(course_create.categories)),
                                check_not_found=True
                                )

    course = Course.model_validate(course_create,
                                   update={"categories": categories,
                                           "instructor_id": current_user.id})
    return save_data_to_db(session, course, dto=CourseResponse)


@courses_router.put(path="/{course_id}",
                    responses={
                        200: {"model": CourseResponse},
                        404: {"description": "Course/Category not found."},
                    }
                    )
async def update_course(
        course_id: UUID,
        course_update: CourseUpdate,
        current_user: Annotated[User, Depends(get_current_user)],
        session: Annotated[Session, Depends(get_session)]
):
    course = get_data_in_db(session, Course,
                            obj_id=course_id,
                            check_not_found=True)

    if current_user.id != course.instructor_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to update course",
        )

    if course_update.categories is not None:
        categories = get_data_in_db(session, Category,
                                    mode='query_all',
                                    query=select(Category)
                                    .where(col(Category.name).in_(course_update.categories)),
                                    check_not_found=True)
        course.categories = categories

    course.sqlmodel_update(obj=course_update.model_dump(exclude_unset=True))
    return save_data_to_db(session, course, dto=CourseResponse)


@courses_router.get("/section/{section_id}", response_model=SectionResponse)
async def get_section(section_id: UUID, session: Annotated[Session, Depends(get_session)]):
    return get_data_in_db(session, Section,
                          obj_id=section_id,
                          dto=SectionResponse,
                          check_not_found=True)


@courses_router.post("/{course_id}/section",
                     responses={
                         200: {"model": SectionResponse},
                         404: {"description": "Course not found."},
                     }
                     )
async def add_section(
        course_id: UUID,
        section_create: SectionCreate,
        current_user: Annotated[User, Depends(get_current_user)],
        session: Annotated[Session, Depends(get_session)]
):
    course = get_data_in_db(session, Course,
                            obj_id=course_id,
                            check_not_found=True)

    if current_user.id != course.instructor_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to update course",
        )

    section = Section.model_validate(section_create, update={"course_section": course})
    return save_data_to_db(session, section, dto=SectionResponse)


@courses_router.get("/lesson/{lesson_id}", response_model=LessonResponse)
async def get_lesson(lesson_id: UUID, session: Annotated[Session, Depends(get_session)]):
    return get_data_in_db(session, Lesson,
                          obj_id=lesson_id,
                          dto=LessonResponse,
                          check_not_found=True)


@courses_router.post("/section/{section_id}/lesson",
                     responses={
                         200: {"model": LessonResponse},
                         404: {"description": "Course/Section not found."},
                     }
                     )
async def add_lesson(
        section_id: UUID,
        lesson_create: LessonCreate,
        current_user: Annotated[User, Depends(get_current_user)],
        session: Annotated[Session, Depends(get_session)]
):
    section = get_data_in_db(session, Section,
                             obj_id=section_id,
                             check_not_found=True)

    if section.course_section.instructor_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to update course",
        )

    if lesson_create.type != 'text':
        lesson_create.text = None

    lesson = Lesson.model_validate(lesson_create, update={"section_lesson": section})
    return save_data_to_db(session, lesson, dto=LessonResponse)


@courses_router.post("/lesson/{lesson_id}/video",
                     responses={
                         200: {"model": LessonResponse},
                         404: {"description": "Lesson not found."},
                     }
                     )
async def upload_lesson_video(
        lesson_id: UUID,
        file: UploadFile,
        background_tasks: BackgroundTasks,
        current_user: Annotated[User, Depends(get_current_user)],
        session: Annotated[Session, Depends(get_session)]
):
    lesson = get_data_in_db(session, Lesson,
                            obj_id=lesson_id,
                            check_not_found=True)

    if lesson.section_lesson.course_section.instructor_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to update course",
        )

    # Use PyAV to get the video's duration
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

    # Transcode the video in the background
    background_tasks.add_task(transcode_video,
                              lesson_id=lesson.id,
                              path=path,
                              duration_seconds=duration_seconds)

    lesson.link = "Uploading"
    return save_data_to_db(session, lesson, dto=LessonResponse)


@courses_router.post("/lesson/{lesson_id}/resource", response_model=LessonResponse)
async def upload_lesson_resource(
        lesson_id: UUID,
        resource_create: LessonResourceDto,
        current_user: Annotated[User, Depends(get_current_user)],
        session: Annotated[Session, Depends(get_session)]
):
    lesson = get_data_in_db(session, Lesson,
                            obj_id=lesson_id,
                            check_not_found=True)

    if lesson.section_lesson.course_section.instructor_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to update course",
        )

    resource = LessonResource.model_validate(resource_create, update={"lesson_resource": lesson})
    save_data_to_db(session, resource)
    return LessonResponse.model_validate(resource.lesson_resource)


@courses_router.get("/quiz/{quiz_id}", response_model=QuizResponse)
async def get_quiz(quiz_id: UUID, session: Annotated[Session, Depends(get_session)]):
    return get_data_in_db(session, Quiz,
                          obj_id=quiz_id,
                          dto=QuizResponse,
                          check_not_found=True)


@courses_router.post("/section/{section_id}/quiz/",
                     responses={
                         200: {"model": QuizResponse},
                         404: {"description": "Course/Section not found."},
                     })
async def add_quiz(
        section_id: UUID,
        quiz_create: QuizCreate,
        current_user: Annotated[User, Depends(get_current_user)]
):
    with Session(engine) as session:
        section = get_data_in_db(session, Section,
                                 obj_id=section_id,
                                 check_not_found=True)

        if section.course_section.instructor_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to update course",
            )

        quiz = Quiz.model_validate(quiz_create, update={"section_quiz": section, "questions": []})
        save_data_to_db(session, quiz)

    quiz_id = quiz.id

    with Session(engine) as session:
        for question_create in quiz_create.questions:
            question = QuizQuestion.model_validate(question_create, update={"quiz_id": quiz_id})
            session.add(question)
        session.commit()

        return get_data_in_db(session, Quiz,
                              obj_id=quiz_id,
                              dto=QuizResponse,
                              check_not_found=True)


@courses_router.get("/category/all", response_model=list[CategoryResponse])
async def get_all_category(session: Annotated[Session, Depends(get_session)]):
    return get_data_in_db(session, Category, mode='all')


@courses_router.post(path="/category",
                     responses={
                         200: {"model": CategoryResponse},
                         409: {"description": "Category already existed."},
                     }
                     )
async def create_category(
        category_create: CategoryCreate,
        current_user: Annotated[User, Depends(get_current_user)],
        session: Annotated[Session, Depends(get_session)]
):
    if not current_user.is_instructor:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to create course",
        )

    get_data_in_db(session, Category,
                   mode='query_one',
                   query=select(Category).where(col(Category.name) == category_create.name),
                   check_existed=True)

    category = Category.model_validate(category_create)
    return save_data_to_db(session, category)
