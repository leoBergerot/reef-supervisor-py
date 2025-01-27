from typing import Annotated, Type

from fastapi import APIRouter, Depends, Security, Query, HTTPException

from app.core.security import get_current_user
from app.core.controllers.parameter import CreateParameterUseCase, UpdateParameterUseCase, ListParameterUseCase
from app.models import ParameterResponse, ParameterRequest
from app.repositories import ParameterRepository, UserRepository
from app.schemas import User

router = APIRouter(
    prefix="/parameters",
    tags=["Parameters"],
)

create_parameter_controller = CreateParameterUseCase(ParameterRepository(), UserRepository())


@router.post("", response_model=ParameterResponse, description="Admin role required")
def create(parameter_request: ParameterRequest,
           current_user: Annotated[User, Security(get_current_user, scopes=['ADMIN'])]):
    return create_parameter_controller.execute(parameter_request.to_core())


update_parameter_controller = UpdateParameterUseCase(ParameterRepository())


@router.put("/{parameter_id}", response_model=ParameterResponse, description="Admin role required")
def update(parameter_id: int, parameter_request: ParameterRequest,
           current_user: Annotated[User, Security(get_current_user, scopes=['ADMIN'])]):
    try:
        return update_parameter_controller.execute(parameter_id, parameter_request)
    except Exception as e:
        error = e.args
        if 'status_code' in error[0]:
            raise HTTPException(
                status_code=error[0].get('status_code'), detail=error[0].get('detail')
            )


list_parameter_controller = ListParameterUseCase(ParameterRepository())


@router.get("", description="Find parameter by ilike name and by ids", response_model=list[ParameterResponse])
def read(parameter_repository: Annotated[ParameterRepository, Depends(ParameterRepository)],
         name: str | None = None,
         ids: Annotated[list[int] | None, Query()] = None):
    return list_parameter_controller.execute(name, ids)
