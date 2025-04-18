import uuid

from fastapi import HTTPException, status
from sqlmodel import Session

from courses.models import Lesson
from data.aws import media_convert_client, cloudfront_url
from data.engine import engine


def get_lesson_in_db(session, lesson_id):
    lesson = session.get(Lesson, lesson_id)

    if lesson is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Lesson not found."
        )

    return lesson


def lesson_uploading(session, lesson: Lesson):
    lesson.link = "Uploading"
    session.add(lesson)
    session.commit()
    session.refresh(lesson)
    return lesson


def transcode_video(lesson_id: uuid.UUID, path: str, duration_seconds: int):
    # Convert video to HLS format
    job = media_convert_client.create_job(
        Role='arn:aws:iam::971422717054:role/service-role/MediaConvert_Default_Role',
        Settings={
            "TimecodeConfig": {
                "Source": "ZEROBASED"
            },
            "OutputGroups": [
                {
                    "CustomName": "Test_group_name",
                    "Name": "Apple HLS",
                    "Outputs": [
                        {
                            "Preset": "System-Avc_16x9_720p_29_97fps_3500kbps",
                            "OutputSettings": {
                                "HlsSettings": {
                                    "SegmentModifier": "segment_test"
                                }
                            },
                            "NameModifier": "output_test"
                        }
                    ],
                    "OutputGroupSettings": {
                        "Type": "HLS_GROUP_SETTINGS",
                        "HlsGroupSettings": {
                            "SegmentLength": 10,
                            "Destination": "s3://ucademic-images-videos-s3/" + path + "hls",
                            "DestinationSettings": {
                                "S3Settings": {
                                    "StorageClass": "STANDARD"
                                }
                            },
                            "MinSegmentLength": 0
                        }
                    }
                }
            ],
            "FollowSource": 1,
            "Inputs": [
                {
                    "AudioSelectors": {
                        "Audio Selector 1": {
                            "DefaultSelection": "DEFAULT"
                        }
                    },
                    "VideoSelector": {},
                    "TimecodeSource": "ZEROBASED",
                    "FileInput": "s3://ucademic-images-videos-s3/" + path + "original"
                }
            ]
        }
    )

    with Session(engine) as session:
        lesson = get_lesson_in_db(session=session, lesson_id=lesson_id)
        # Update the database object
        if lesson.section_lesson.course_section.duration is not None:
            if lesson.duration is not None and lesson.duration != 0:
                lesson.section_lesson.course_section.duration -= lesson.duration
            lesson.section_lesson.course_section.duration += duration_seconds
        else:
            lesson.section_lesson.course_section.duration = duration_seconds

        if lesson.section_lesson.course_section.lessons is not None:
            if lesson.duration is not None and lesson.duration != 0:
                lesson.section_lesson.course_section.duration -= 1
            lesson.section_lesson.course_section.lessons += 1
        else:
            lesson.section_lesson.course_section.lessons = 1

        lesson.link = cloudfront_url + path + 'hls.m3u8'
        lesson.duration = duration_seconds

        session.add(lesson)
        session.commit()
        session.refresh(lesson)
