from typing import Annotated

from fastapi import APIRouter, Security, Depends

from app.core.controllers.tank import CreateTankUseCase, ListTankUseCase
from app.core.security import get_current_user
from app.models import TankResponse, TankRequest
from app.repositories import TankRepository
from app.schemas import User

router = APIRouter(
    prefix="/tanks",
    tags=["Tanks"]
)

create_tank_controller = CreateTankUseCase(TankRepository())


@router.post("", response_model=TankResponse, description="Create tank associated to user authenticated")
def create(tank_request: TankRequest,
           current_user: Annotated[User, Security(get_current_user, scopes=["USER"])]):
    return create_tank_controller.execute(tank_request.to_core(), current_user.to_core_no_relation())


list_tank_controller = ListTankUseCase(TankRepository())


@router.get("", response_model=list[TankResponse], description="Get tank associated to user authenticated")
def read(current_user: Annotated[User, Security(get_current_user, scopes=["USER"])]):
    return list_tank_controller.execute(current_user.to_core_no_relation())
