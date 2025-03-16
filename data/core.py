from pydantic.alias_generators import to_camel
from sqlmodel import SQLModel


class DtoModel(SQLModel):
    class Config:
        populate_by_name = True
        alias_generator = to_camel
