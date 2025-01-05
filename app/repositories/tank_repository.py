from typing import Sequence

from app.db.session import engine
from app.models import TankRequest
from app.schemas import Tank, User
from sqlmodel import Session, select, col


class TankRepository:

    def create(self, tank_request: TankRequest, user: User) -> Tank:
        tank = Tank(**tank_request.model_dump())
        tank.user_id = user.id
        with Session(engine) as session:
            session.add(tank)
            session.commit()
            session.refresh(tank)

        return tank

    def get_all(self, user) -> Sequence[Tank]:
        with Session(engine) as session:
            return session.exec(
                select(Tank).filter(col(Tank.user_id) == user.id)
            ).all()
