from typing import Literal, TypeVar
from sqlmodel.sql.expression import SelectOfScalar
from sqlmodel import Session

from data.engine import engine

T = TypeVar("T")
D = TypeVar("D")


def run_sql_select_query(query: SelectOfScalar[T], mode: Literal["one", "all"], dto: D | None = None):
    """Specify dto type if getting DetachedInstanceError"""
    with Session(engine) as session:
        if mode == "one":
            temp = session.exec(query).first()
            if dto:
                return dto.model_validate(temp)
            else:
                return temp
        elif mode == "all":
            temps = session.exec(query).all()
            if dto:
                return [dto.model_validate(temp) for temp in temps]
            else:
                return temps


def run_sql_save_query(obj: [T], dto: D | None = None) -> T:
    """Specify dto type if getting DetachedInstanceError"""
    with Session(engine) as session:
        session.add(obj)
        session.commit()
        session.refresh(obj)
        if dto:
            return dto.model_validate(obj)
        return obj

