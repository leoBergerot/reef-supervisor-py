from typing import Annotated, Type
from fastapi import Depends
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.db.session import get_db
from app.schemas import Parameter


class ParameterRepository:
    def __init__(self, db: Annotated[Session, Depends(get_db)]):
        self.db = db

    def get_all(self) -> list[Type[Parameter]]:
        return self.db.query(Parameter).all()

    def get_by_id(self, parameter_id: int) -> Parameter:
        return self.db.query(Parameter).filter(Parameter.id == parameter_id).first()

    def get_by_filter(self, name: str | None, ids: list[int] | None) -> list[Type[Parameter]]:
        query = self.db.query(Parameter)
        conditions = []
        if name is not None:
            conditions.append(Parameter.name.ilike(f'%{name}%'))
        if ids is not None:
            conditions.append(Parameter.id.in_(ids))

        if len(conditions) > 0:
            query = query.filter(and_(*conditions))

        return query.all()
