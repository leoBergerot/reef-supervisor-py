from app.core.entities import User
from app.core.models import TankResponse
from app.repositories import TankRepository


class ListTankUseCase:

    def __init__(self, tank_repository: TankRepository):
        self.tank_repository = tank_repository

    def execute(self, user: User) -> list[TankResponse]:
        return [tank.to_response_view() for tank in self.tank_repository.get_all(user)]
