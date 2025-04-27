import uuid

from sqlmodel import Session

from courses.models import Lesson
from data.aws import media_convert_client, cloudfront_url
from data.engine import engine
from data.service import get_data_in_db


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
                    "Name": "Apple HLS",
                    "Outputs": [
                        {
                            "ContainerSettings": {
                                "Container": "M3U8",
                                "M3u8Settings": {}
                            },
                            "VideoDescription": {
                                "Height": 1080,
                                "CodecSettings": {
                                    "Codec": "H_264",
                                    "H264Settings": {
                                        "MaxBitrate": 5000000,
                                        "RateControlMode": "QVBR",
                                        "SceneChangeDetect": "TRANSITION_DETECTION"
                                    }
                                }
                            },
                            "AudioDescriptions": [
                                {
                                    "AudioSourceName": "Audio Selector 1",
                                    "CodecSettings": {
                                        "Codec": "AAC",
                                        "AacSettings": {
                                            "Bitrate": 96000,
                                            "CodingMode": "CODING_MODE_2_0",
                                            "SampleRate": 48000
                                        }
                                    }
                                }
                            ],
                            "OutputSettings": {
                                "HlsSettings": {}
                            },
                            "NameModifier": "_1080p"
                        },
                        {
                            "ContainerSettings": {
                                "Container": "M3U8",
                                "M3u8Settings": {}
                            },
                            "VideoDescription": {
                                "Height": 720,
                                "CodecSettings": {
                                    "Codec": "H_264",
                                    "H264Settings": {
                                        "MaxBitrate": 5000000,
                                        "RateControlMode": "QVBR",
                                        "SceneChangeDetect": "TRANSITION_DETECTION"
                                    }
                                }
                            },
                            "AudioDescriptions": [
                                {
                                    "AudioSourceName": "Audio Selector 1",
                                    "CodecSettings": {
                                        "Codec": "AAC",
                                        "AacSettings": {
                                            "Bitrate": 96000,
                                            "CodingMode": "CODING_MODE_2_0",
                                            "SampleRate": 48000
                                        }
                                    }
                                }
                            ],
                            "OutputSettings": {
                                "HlsSettings": {}
                            },
                            "NameModifier": "_720p"
                        },
                        {
                            "ContainerSettings": {
                                "Container": "M3U8",
                                "M3u8Settings": {}
                            },
                            "VideoDescription": {
                                "Height": 360,
                                "CodecSettings": {
                                    "Codec": "H_264",
                                    "H264Settings": {
                                        "MaxBitrate": 5000000,
                                        "RateControlMode": "QVBR",
                                        "SceneChangeDetect": "TRANSITION_DETECTION"
                                    }
                                }
                            },
                            "AudioDescriptions": [
                                {
                                    "AudioSourceName": "Audio Selector 1",
                                    "CodecSettings": {
                                        "Codec": "AAC",
                                        "AacSettings": {
                                            "Bitrate": 96000,
                                            "CodingMode": "CODING_MODE_2_0",
                                            "SampleRate": 48000
                                        }
                                    }
                                }
                            ],
                            "OutputSettings": {
                                "HlsSettings": {}
                            },
                            "NameModifier": "_360p"
                        }
                    ],
                    "OutputGroupSettings": {
                        "Type": "HLS_GROUP_SETTINGS",
                        "HlsGroupSettings": {
                            "SegmentLength": 10,
                            "Destination": "s3://ucademic-images-videos-s3/",
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
        lesson = get_data_in_db(session, Lesson, obj_id=lesson_id)

        lesson.link = cloudfront_url + path + 'hls.m3u8'
        lesson.duration = duration_seconds

        session.add(lesson)
        session.commit()
        session.refresh(lesson)

