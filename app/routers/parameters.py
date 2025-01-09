from typing import Annotated, Type

from fastapi import APIRouter, Depends, Security, HTTPException, Query

from app.core.security import get_current_user
from app.core.use_cases.parameter import CreateParameterUseCase
from app.models import ParameterResponse, ParameterRequest
from app.repositories import ParameterRepository
from app.schemas import User

router = APIRouter(
    prefix="/parameters",
    tags=["Parameters"],
)


create_parameter_use_case = CreateParameterUseCase(ParameterRepository())

@router.post("", response_model=ParameterResponse, description="Admin role required")
def create(parameter_request: ParameterRequest,
           current_user: Annotated[User, Security(get_current_user, scopes=['ADMIN'])]):
    return create_parameter_use_case.execute(parameter_request.to_application())


# @router.put("/{parameter_id}", response_model=ParameterResponse, description="Admin role required")
# def update(parameter_id: int, parameter_request: ParameterRequest,
#            parameter_manager: Annotated[ParameterManager, Depends(ParameterManager)],
#            current_user: Annotated[User, Security(get_current_user, scopes=['ADMIN'])],
#            parameter_repository: Annotated[ParameterRepository, Depends(ParameterRepository)]):
#     parameter = parameter_repository.get_by_id(parameter_id)
#     if parameter is None:
#         raise HTTPException(
#             status_code=404, detail="Parameter not found"
#         )
#
#     return ParameterResponse.model_validate(parameter_manager.update_persist(parameter, parameter_request),
#                                             from_attributes=True)


@router.get("", description="Find parameter by ilike name and by ids", response_model=list[ParameterResponse])
def read(parameter_repository: Annotated[ParameterRepository, Depends(ParameterRepository)],
         name: str | None = None,
         ids: Annotated[list[int] | None, Query()] = None):
    parameters = parameter_repository.get_by_filter(name=name, ids=ids)
    return [ParameterResponse.model_validate(parameter, from_attributes=True) for parameter in parameters]
