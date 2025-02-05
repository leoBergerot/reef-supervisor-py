from app.core.entities import User
from app.core.models import TankRequest, TankResponse
from app.repositories import TankRepository


class CreateTankUseCase:

    def __init__(self, tank_repository: TankRepository):
        self.tank_repository = tank_repository

    def execute(self, tank_request: TankRequest, user: User) -> TankResponse:
        return self.tank_repository.create(tank_request, user).to_response_view()
