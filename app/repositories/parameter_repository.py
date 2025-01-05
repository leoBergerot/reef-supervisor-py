from typing import Sequence
from sqlmodel import Session, and_, select, col
from app.db.session import engine
from app.schemas import Parameter


class ParameterRepository:
    def get_all(self) -> Sequence[Parameter]:
        with Session(engine) as session:
            return session.exec(select(Parameter)).all()

    def get_by_id(self, parameter_id: int) -> Parameter:
        with Session(engine) as session:
            return session.exec(select(Parameter).filter(col(Parameter.id == parameter_id))).first()

    def get_by_filter(self, name: str | None, ids: list[int] | None) -> Sequence[Parameter]:
        with Session(engine) as session:
            query = select(Parameter)
            conditions = []
            if name is not None:
                conditions.append(col(Parameter.name).ilike(f'%{name}%'))
            if ids is not None:
                conditions.append(col(Parameter.id).in_(ids))

            if len(conditions) > 0:
                query = query.filter(and_(*conditions))

            return session.exec(query).all()
