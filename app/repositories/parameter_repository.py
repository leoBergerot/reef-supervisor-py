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
            rows = session.exec(
                select(Parameter).where(col(Parameter.is_custom) == False)  # noqa: E712
            ).all()
            return [parameter.to_core() for parameter in rows]

    def get_by_id(self, parameter_id: int) -> None | ParameterDomain:
        with Session(engine) as session:
            parameter = session.exec(
                select(Parameter).filter(col(Parameter.id) == parameter_id)
            ).first()
            if parameter:
                return parameter.to_core()
            return None

    def get_by_filter(self, name: str | None, ids: list[int] | None) -> Sequence[ParameterDomain]:
        with Session(engine) as session:
            query = select(Parameter).where(col(Parameter.is_custom) == False)  # noqa: E712
            conditions = []
            if name is not None:
                conditions.append(col(Parameter.name).ilike(f"%{name}%"))
            if ids is not None:
                conditions.append(col(Parameter.id).in_(ids))

            if len(conditions) > 0:
                query = query.filter(and_(*conditions))

            return [parameter.to_core() for parameter in session.exec(query).all()]

    def get_defaults_for_water_type(self, water_type: str) -> Sequence[ParameterDomain]:
        with Session(engine) as session:
            query = select(Parameter).where(col(Parameter.is_custom) == False)  # noqa: E712
            if water_type == "seawater":
                query = query.where(col(Parameter.for_seawater) == True)  # noqa: E712
            elif water_type == "freshwater":
                query = query.where(col(Parameter.for_freshwater) == True)  # noqa: E712
            else:
                return []
            return [parameter.to_core() for parameter in session.exec(query).all()]

    def get_catalog_by_ids(self, parameter_ids: list[int]) -> Sequence[ParameterDomain]:
        if not parameter_ids:
            return []
        with Session(engine) as session:
            rows = session.exec(
                select(Parameter).where(
                    and_(
                        col(Parameter.id).in_(parameter_ids),
                        col(Parameter.is_custom) == False,  # noqa: E712
                    )
                )
            ).all()
            return [parameter.to_core() for parameter in rows]

    def create_persist(self, parameter_request: ParameterRequest) -> ParameterDomain:
        parameter = Parameter().from_core_request(parameter_request)
        with Session(engine) as session:
            session.add(parameter)
            session.commit()
            session.refresh(parameter)

        return parameter.to_core()

    def update_persist(self, parameter_core: ParameterDomain, parameter_request: ParameterRequest) -> ParameterDomain:
        parameter_core.update(parameter_request)
        parameter = Parameter().from_core(parameter_core)
        with Session(engine) as session:
            parameter = session.merge(parameter)
            session.commit()
            session.refresh(parameter)
        return parameter.to_core()

    def create_custom(self, name: str, unit: str) -> ParameterDomain:
        parameter = Parameter(
            name=name,
            sub_name=unit,
            need_value=True,
            for_seawater=False,
            for_freshwater=False,
            is_custom=True,
        )
        with Session(engine) as session:
            session.add(parameter)
            session.commit()
            session.refresh(parameter)
            return parameter.to_core()

    def delete_by_ids(self, parameter_ids: list[int]) -> None:
        if not parameter_ids:
            return
        with Session(engine) as session:
            rows = session.exec(
                select(Parameter).where(
                    and_(
                        col(Parameter.id).in_(parameter_ids),
                        col(Parameter.is_custom) == True,  # noqa: E712
                    )
                )
            ).all()
            for row in rows:
                session.delete(row)
            session.commit()
