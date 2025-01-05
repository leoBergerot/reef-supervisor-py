from typing import Annotated

from fastapi import APIRouter, Security, Depends

from app.core.security import get_current_user
from app.models import TankResponse, TankRequest
from app.repositories import TankRepository
from app.schemas import User

router = APIRouter(
    prefix="/tanks",
    tags=["Tanks"]
)


@router.post("", response_model=TankResponse, description="Create tank associated to user authenticated")
def create(tank_request: TankRequest,
           current_user: Annotated[User, Security(get_current_user, scopes=["USER"])],
           tank_repository: Annotated[TankRepository, Depends(TankRepository)]):
    return TankResponse.model_validate(tank_repository.create(tank_request, current_user), from_attributes=True)


@router.get("", response_model=list[TankResponse], description="Get tank associated to user authenticated")
def read(current_user: Annotated[User, Security(get_current_user, scopes=["USER"])],
         tank_repository: Annotated[TankRepository, Depends(TankRepository)]):
    return [TankResponse.model_validate(tank, from_attributes=True) for tank in tank_repository.get_all(current_user)]
