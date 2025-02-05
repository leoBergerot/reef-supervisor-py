from app.core.entities import User, Tank
from app.core.models import TankRequest


class TankRepository:

    def create(self, tank_request: TankRequest, user: User) -> Tank:
        raise NotImplementedError()

    def get_all(self, user) -> list[Tank]:
        raise NotImplementedError()

    @staticmethod
    def is_tank_owned_by_user(tank_id: int, user: User) -> bool:
        raise NotImplementedError()
