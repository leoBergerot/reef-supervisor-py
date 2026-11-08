from pathlib import Path

from app.core.models import TankRequest
from app.core.repositories import TankRepository as DomainTankRepository
from app.core.entities import Tank as TankCore
from app.core.entities import User as UserCore
from app.db.session import engine
from app.schemas import Tank, User, Measure
from sqlmodel import Session, select, col, and_


class TankRepository(DomainTankRepository):

    def create(self, tank_request: TankRequest, user: UserCore) -> TankCore:
        tank = Tank().from_request(tank_request)
        tank.user_id = user.id
        with Session(engine) as session:
            session.add(tank)
            session.commit()
            session.refresh(tank)

        return tank.to_core()

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
            session.delete(tank)
            session.commit()
        if photo_path:
            Path(photo_path).unlink(missing_ok=True)
        return True
