from app.core.models import TankRequest
from app.core.repositories import TankRepository as DomainTankRepository
from app.core.entities import Tank as TankCore
from app.core.entities import User as UserCore
from app.db.session import engine
from app.schemas import Tank, User
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
