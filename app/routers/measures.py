from http.client import responses
from typing import Annotated
from unittest.mock import patch

from fastapi import APIRouter, Depends, HTTPException, status, Security

from app.core.security import get_current_user
from app.managers import MeasureManager
from app.models import MeasureResponse, MeasureRequest
from app.models.measure import MeasureListPaginateResponse, MeasureRequestValue
from app.repositories import TankRepository, MeasureRepository
from app.schemas import User

router = APIRouter(
    prefix="/measures",
    tags=["Measures"]
)


@router.get("", response_model=MeasureListPaginateResponse, description="Read measure according to user authenticated")
def read(current_user: Annotated[User, Security(get_current_user, scopes=['USER'])],
         measure_repository: Annotated[MeasureRepository, Depends(MeasureRepository)],
         page: int = 1,
         parameter_id: int | None = None,
         tank_id: int | None = None,
         ):
    measures = measure_repository.get_filter(current_user, parameter_id, tank_id, page)
    return MeasureListPaginateResponse(
        **{'data': [MeasureResponse.model_validate(measure.model_dump(), from_attributes=True) for measure in
                    measures['results']],
           'total_page': measures['total_page'], 'total': measures['total']})


@router.patch("/{measure_id}", response_model=MeasureResponse, description="Update measure value")
def updateValue(measure_id: int,
                measure_request: MeasureRequestValue,
                current_user: Annotated[User, Security(get_current_user, scopes=["USER"])],
                measure_repository: Annotated[MeasureRepository, Depends(MeasureRepository)],
                measure_manager: Annotated[MeasureManager, Depends(MeasureManager)]):
    measure = measure_repository.get_measure_by_id_and_user(measure_id, current_user)
    if measure is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Measure ID {measure_id} does not belong to User ID {current_user.id}")
    return MeasureResponse.model_validate(measure_manager.updateValue(measure_request, measure).model_dump(),
                                          from_attributes=True)


@router.post("", response_model=MeasureResponse, description="Create measure link to user authenticated")
def create(measure_request: MeasureRequest,
           current_user: Annotated[User, Security(get_current_user, scopes=['USER'])],
           tank_repository: Annotated[TankRepository, Depends(TankRepository)],
           measure_manager: Annotated[MeasureManager, Depends(MeasureManager)]):
    if not tank_repository.is_tank_owned_by_user(measure_request.tank_id, current_user):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Tank ID {measure_request.tank_id} does not belong to User ID {current_user.id}")
    measure = measure_manager.create(measure_request)

    return MeasureResponse.model_validate(measure.model_dump(), from_attributes=True)
