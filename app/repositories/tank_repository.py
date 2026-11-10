from pathlib import Path

from app.core.models import TankRequest
from app.core.repositories import TankRepository as DomainTankRepository
from app.core.entities import Tank as TankCore
from app.core.entities import User as UserCore
from app.db.session import engine
from app.repositories.parameter_repository import ParameterRepository
from app.repositories.tank_parameter_repository import TankParameterRepository
from app.schemas import Tank, Measure, Parameter, TankParameter
from sqlmodel import Session, select, col, and_


class TankRepository(DomainTankRepository):

    def create(self, tank_request: TankRequest, user: UserCore) -> TankCore:
        parameter_repository = ParameterRepository()
        tank_parameter_repository = TankParameterRepository()

        if tank_request.enabled_parameter_ids is None:
            defaults = parameter_repository.get_defaults_for_water_type(tank_request.water_type)
            enabled_ids = [parameter.id for parameter in defaults]
        else:
            catalog = parameter_repository.get_catalog_by_ids(tank_request.enabled_parameter_ids)
            found = {parameter.id for parameter in catalog}
            unknown = [parameter_id for parameter_id in tank_request.enabled_parameter_ids if parameter_id not in found]
            if unknown:
                raise ValueError(f"Unknown catalog parameter ids: {unknown}")
            enabled_ids = list(dict.fromkeys(tank_request.enabled_parameter_ids))

        tank = Tank().from_request(tank_request)
        tank.user_id = user.id
        with Session(engine) as session:
            session.add(tank)
            session.commit()
            session.refresh(tank)
            tank_id = tank.id
            core = tank.to_core()

        tank_parameter_repository.seed_for_tank(tank_id, enabled_ids, enabled=True)

        for custom in tank_request.custom_parameters:
            parameter = parameter_repository.create_custom(custom["name"], custom["unit"])
            tank_parameter_repository.create(tank_id, parameter.id, enabled=True)

        return core

    def get_all(self, user: UserCore) -> list[TankCore]:
        with Session(engine) as session:
            return [tank.to_core() for tank in session.exec(
                select(Tank).filter(col(Tank.user_id) == user.id)
            ).all()]

    @staticmethod
    def is_tank_owned_by_user(tank_id: int, user: UserCore) -> bool:
        with Session(engine) as session:
            return session.exec(select(Tank).filter(
                and_(
                    col(Tank.id) == tank_id,
                    col(Tank.user_id) == user.id)
            )).first() is not None

    def get_for_user(self, tank_id: int, user: UserCore) -> TankCore | None:
        with Session(engine) as session:
            tank = session.exec(select(Tank).filter(
                and_(col(Tank.id) == tank_id, col(Tank.user_id) == user.id)
            )).first()
            return tank.to_core() if tank else None

    def update_name(self, tank_id: int, user: UserCore, name: str) -> TankCore | None:
        with Session(engine) as session:
            tank = session.exec(select(Tank).filter(
                and_(col(Tank.id) == tank_id, col(Tank.user_id) == user.id)
            )).first()
            if tank is None:
                return None
            tank.name = name
            session.add(tank)
            session.commit()
            session.refresh(tank)
            return tank.to_core()

    def set_photo_path(self, tank_id: int, user: UserCore, photo_path: str) -> TankCore | None:
        with Session(engine) as session:
            tank = session.exec(select(Tank).filter(
                and_(col(Tank.id) == tank_id, col(Tank.user_id) == user.id)
            )).first()
            if tank is None:
                return None
            previous = tank.photo_path
            tank.photo_path = photo_path
            session.add(tank)
            session.commit()
            session.refresh(tank)
            stored = tank.to_core()
        if previous and previous != photo_path:
            Path(previous).unlink(missing_ok=True)
        return stored

    def delete_for_user(self, tank_id: int, user: UserCore) -> bool:
        with Session(engine) as session:
            tank = session.exec(select(Tank).filter(
                and_(col(Tank.id) == tank_id, col(Tank.user_id) == user.id)
            )).first()
            if tank is None:
                return False
            photo_path = tank.photo_path

            measures = session.exec(select(Measure).where(col(Measure.tank_id) == tank.id)).all()
            for measure in measures:
                session.delete(measure)
            session.flush()

            linked = session.exec(
                select(TankParameter, Parameter)
                .join(Parameter, col(Parameter.id) == col(TankParameter.parameter_id))
                .where(col(TankParameter.tank_id) == tank.id)
            ).all()
            custom_parameter_ids = [
                parameter.id for _, parameter in linked if parameter.is_custom
            ]
            for tank_parameter, _ in linked:
                session.delete(tank_parameter)
            session.flush()

            session.delete(tank)
            session.flush()

            for parameter_id in custom_parameter_ids:
                parameter = session.get(Parameter, parameter_id)
                if parameter is not None:
                    session.delete(parameter)
            session.commit()

        if photo_path:
            Path(photo_path).unlink(missing_ok=True)
        return True
