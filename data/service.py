import typing
from typing import TypeVar, Any, Literal, Type

from fastapi import HTTPException, status
from sqlmodel import Session, select
from sqlmodel.sql.expression import SelectOfScalar

T = TypeVar('T')
D = TypeVar('D')


def get_data_in_db(session: Session,
                   obj_type: Type[T],
                   mode: Literal['id', 'query_one', 'query_all', 'all'] = 'id',
                   obj_id: Any | None = None,
                   query: SelectOfScalar[T] | None = None,
                   dto: D | None = None,
                   check_not_found: bool = False,
                   check_existed: bool = False,
                   ) -> T | list[T] | D | list[D]:
    temp = None
    match mode:
        case 'id':
            temp = session.get(obj_type, obj_id)
        case 'query_one':
            temp = session.exec(query).first()
        case 'query_all':
            temp = session.exec(query).all()
        case 'all':
            temp = session.exec(select(obj_type)).all()

    if check_not_found and not temp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=typing.get_args(obj_type)[0].__name__ + 'not found'
        )

    if check_existed and temp:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=typing.get_args(obj_type)[0].__name__ + 'already existed'
        )

    if not dto:
        return temp
    else:
        if mode == 'all' or mode == 'query_all':
            return [dto.model_validate(t) for t in temp]
        else:
            return dto.model_validate(temp)


def save_data_to_db(session: Session,
                    obj: T,
                    dto: D | None = None,
                    ) -> T | D:
    session.add(obj)
    session.commit()
    session.refresh(obj)
    if dto:
        return dto.model_validate(obj)
    return obj
