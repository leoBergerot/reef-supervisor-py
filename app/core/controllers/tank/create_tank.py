from fastapi import HTTPException, status

from app.core.entities import User
from app.core.models import TankRequest, TankResponse
from app.repositories import TankRepository


class CreateTankUseCase:

    def __init__(self, tank_repository: TankRepository):
        self.tank_repository = tank_repository

    def execute(self, tank_request: TankRequest, user: User) -> TankResponse:
        try:
            return self.tank_repository.create(tank_request, user).to_response_view()
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(exc)) from exc
