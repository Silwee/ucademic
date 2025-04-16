import uuid

from pydantic import AliasGenerator
from pydantic.alias_generators import to_camel
from sqlmodel import SQLModel


class DtoModel(SQLModel):
    class Config:
        populate_by_name = True
        alias_generator = AliasGenerator(
            validation_alias=to_camel,
            serialization_alias=to_camel
        )


def new_uuid() -> uuid.UUID:
    # Note: Work around UUIDs with leading zeros: https://github.com/tiangolo/sqlmodel/issues/25
    # by making sure uuid str does not start with a leading 0
    val = uuid.uuid4()
    while val.hex[0] == '0':
        val = uuid.uuid4()

    return val
