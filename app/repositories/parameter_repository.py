from typing import Sequence
from sqlmodel import Session, and_, select, col

from app.db.session import engine
from app.core.models import ParameterRequest
from app.core.entities import Parameter as ParameterDomain
from app.core.repositories import ParameterRepository as DomainParameterRepository
from app.schemas import Parameter


class ParameterRepository(DomainParameterRepository):
    def get_all(self) -> Sequence[ParameterDomain]:
        with Session(engine) as session:
            return session.exec(select(Parameter)).all()

    def get_by_id(self, parameter_id: int) -> ParameterDomain:
        with Session(engine) as session:
            return session.exec(select(Parameter).filter(col(Parameter.id) == parameter_id)).first()

    def get_by_filter(self, name: str | None, ids: list[int] | None) -> Sequence[ParameterDomain]:
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

    def create_persist(self, parameter_request: ParameterRequest) -> ParameterDomain:
        parameter = Parameter().from_core_request(parameter_request)
        with Session(engine) as session:
            session.add(parameter)
            session.commit()
            session.refresh(parameter)

        return parameter

    def update_persist(self, parameter: Parameter, parameter_request: ParameterRequest) -> ParameterDomain:
        parameter = parameter.model_copy(update=parameter_request.model_dump())
        with Session(engine) as session:
            parameter = session.merge(parameter)
            session.commit()
            session.refresh(parameter)

        return parameter

    # def _update_user_preferences(self, parameter: Parameter):
    #     with Session(engine) as session:
    #         users = self.user_repository.get_all()
    #         for user in users:
    #             user.preferences.append(Preference(parameter_id=parameter.id, enabled=True))
    #             session.add(user)
    #         session.commit()