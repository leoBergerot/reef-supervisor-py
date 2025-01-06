from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.security import get_current_user
from app.managers import MeasureManager
from app.models import MeasureResponse, MeasureRequest
from app.repositories import TankRepository
from app.schemas import User

router = APIRouter(
    prefix="/measures",
    tags=["Measures"]
)


@router.post("", response_model=MeasureResponse, description="Create measure link to user authenticated")
def create(measure_request: MeasureRequest,
           current_user: Annotated[User, Depends(get_current_user)],
           tank_repository: Annotated[TankRepository, Depends(TankRepository)],
           measure_manager: Annotated[MeasureManager, Depends(MeasureManager)]):
    if not tank_repository.is_tank_owned_by_user(measure_request.tank_id, current_user):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Tank ID {measure_request.tank_id} does not belong to User ID {current_user.id}", )
    measure = measure_manager.create(measure_request)

    return MeasureResponse.model_validate(measure, from_attributes=True)
