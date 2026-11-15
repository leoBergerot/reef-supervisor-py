from typing import Annotated, Literal

from fastapi import APIRouter, Security, Query, HTTPException

from app.core.security import get_current_user
from app.core.controllers.parameter import CreateParameterUseCase, UpdateParameterUseCase, ListParameterUseCase
from app.defaults import list_default_ranges, resolve_default_range
from app.models import ParameterResponse, ParameterRequest, ParameterRange, ParameterRangeEntry
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
        return update_parameter_controller.execute(parameter_id, parameter_request.to_core())
    except Exception as e:
        error = e.args
        if error and isinstance(error[0], dict) and 'status_code' in error[0]:
            raise HTTPException(
                status_code=error[0].get('status_code'), detail=error[0].get('detail')
            )
        raise


list_parameter_controller = ListParameterUseCase(ParameterRepository())


def _to_parameter_response(parameter, water_type: str | None = None) -> ParameterResponse:
    band = resolve_default_range(parameter.name, water_type) if water_type else None
    return ParameterResponse(
        id=parameter.id,
        name=parameter.name,
        sub_name=parameter.sub_name,
        need_value=parameter.need_value,
        for_seawater=getattr(parameter, "for_seawater", True),
        for_freshwater=getattr(parameter, "for_freshwater", True),
        is_custom=getattr(parameter, "is_custom", False),
        range=(
            ParameterRange(
                min=band["min"],
                max=band["max"],
                soft_min=band.get("soft_min"),
                soft_max=band.get("soft_max"),
            )
            if band
            else None
        ),
    )


@router.get(
    "/ranges",
    response_model=list[ParameterRangeEntry],
    description="Default recommended min/max bands by water type (display warnings only)",
)
def read_ranges(
    current_user: Annotated[User, Security(get_current_user, scopes=["USER"])],
    water_type: Annotated[Literal["seawater", "freshwater"], Query()] = "seawater",
):
    return [ParameterRangeEntry(**row) for row in list_default_ranges(water_type)]


@router.get("", description="Find parameter by ilike name and by ids", response_model=list[ParameterResponse])
def read(
    current_user: Annotated[User, Security(get_current_user, scopes=["USER"])],
    name: str | None = None,
    ids: Annotated[list[int] | None, Query()] = None,
    water_type: Annotated[Literal["seawater", "freshwater"] | None, Query()] = None,
):
    parameters = list_parameter_controller.execute(name, ids)
    return [_to_parameter_response(parameter, water_type) for parameter in parameters]
