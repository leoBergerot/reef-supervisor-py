from typing import Annotated

from fastapi import APIRouter, File, HTTPException, Response, Security, UploadFile, status
from fastapi.responses import FileResponse

from app.core.controllers.tank import CreateTankUseCase, ListTankUseCase
from app.core.security import get_current_user
from app.models import (
    TankResponse,
    TankRequest,
    TankRenameRequest,
    TankParameterResponse,
    TankParameterPatchRequest,
    CustomTankParameterRequest,
    ParameterResponse,
)
from app.repositories import TankRepository, TankParameterRepository, ParameterRepository
from app.schemas import User
from app.storage import photo_media_type, save_tank_photo

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


def _owned_tank_or_404(tank_id: int, current_user: User):
    tank = TankRepository().get_for_user(tank_id, current_user.to_core_no_relation())
    if tank is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tank not found")
    return tank


def _tank_parameter_response(tank_parameter, parameter) -> TankParameterResponse:
    return TankParameterResponse(
        id=tank_parameter.id,
        enabled=tank_parameter.enabled,
        is_custom=parameter.is_custom,
        parameter=ParameterResponse(
            id=parameter.id,
            name=parameter.name,
            sub_name=parameter.sub_name,
            need_value=parameter.need_value,
            for_seawater=parameter.for_seawater,
            for_freshwater=parameter.for_freshwater,
            is_custom=parameter.is_custom,
        ),
    )


@router.get(
    "/{tank_id}/parameters",
    response_model=list[TankParameterResponse],
    description="List parameters configured for a tank (catalog defaults and customs)",
)
def list_tank_parameters(
    tank_id: int,
    current_user: Annotated[User, Security(get_current_user, scopes=["USER"])],
):
    _owned_tank_or_404(tank_id, current_user)
    rows = TankParameterRepository().list_for_tank(tank_id)
    return [_tank_parameter_response(tank_parameter, parameter) for tank_parameter, parameter in rows]


@router.patch(
    "/{tank_id}/parameters",
    response_model=list[TankParameterResponse],
    description="Enable or disable catalog/custom parameters for a tank (upsert for catalog)",
)
def patch_tank_parameters(
    tank_id: int,
    body: TankParameterPatchRequest,
    current_user: Annotated[User, Security(get_current_user, scopes=["USER"])],
):
    _owned_tank_or_404(tank_id, current_user)
    parameter_repository = ParameterRepository()
    tank_parameter_repository = TankParameterRepository()

    for item in body.parameters:
        parameter = parameter_repository.get_by_id(item.parameter_id)
        if parameter is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail=f"Unknown parameter id: {item.parameter_id}",
            )
        if parameter.is_custom:
            existing = tank_parameter_repository.get_for_tank_parameter(tank_id, item.parameter_id)
            if existing is None:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                    detail=f"Custom parameter {item.parameter_id} does not belong to this tank",
                )
            tank_parameter_repository.upsert_enabled(tank_id, item.parameter_id, item.enabled)
        else:
            tank_parameter_repository.upsert_enabled(tank_id, item.parameter_id, item.enabled)

    rows = tank_parameter_repository.list_for_tank(tank_id)
    return [_tank_parameter_response(tank_parameter, parameter) for tank_parameter, parameter in rows]


@router.post(
    "/{tank_id}/parameters/custom",
    response_model=TankParameterResponse,
    description="Create a custom numeric parameter for a tank",
)
def create_custom_tank_parameter(
    tank_id: int,
    body: CustomTankParameterRequest,
    current_user: Annotated[User, Security(get_current_user, scopes=["USER"])],
):
    _owned_tank_or_404(tank_id, current_user)
    parameter = ParameterRepository().create_custom(body.name, body.unit)
    tank_parameter = TankParameterRepository().create(tank_id, parameter.id, enabled=True)
    return TankParameterResponse(
        id=tank_parameter.id,
        enabled=tank_parameter.enabled,
        is_custom=True,
        parameter=ParameterResponse(
            id=parameter.id,
            name=parameter.name,
            sub_name=parameter.sub_name,
            need_value=parameter.need_value,
            for_seawater=parameter.for_seawater,
            for_freshwater=parameter.for_freshwater,
            is_custom=True,
        ),
    )


@router.patch("/{tank_id}", response_model=TankResponse, description="Rename a tank owned by the authenticated user")
def update(tank_id: int, tank_request: TankRenameRequest,
           current_user: Annotated[User, Security(get_current_user, scopes=["USER"])]):
    tank = TankRepository().update_name(tank_id, current_user.to_core_no_relation(), tank_request.name)
    if tank is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tank not found")
    return tank.to_response_view()


@router.delete("/{tank_id}", status_code=status.HTTP_204_NO_CONTENT,
               description="Delete a tank, its measures and its photo")
def delete(tank_id: int, current_user: Annotated[User, Security(get_current_user, scopes=["USER"])]):
    deleted = TankRepository().delete_for_user(tank_id, current_user.to_core_no_relation())
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tank not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.patch("/{tank_id}/photo", response_model=TankResponse,
              description="Upload a tank photo (png, gif, svg, jpeg, jpg)")
def upload_photo(tank_id: int, current_user: Annotated[User, Security(get_current_user, scopes=["USER"])],
                 file: UploadFile = File(...)):
    _owned_tank_or_404(tank_id, current_user)
    photo_path = save_tank_photo(tank_id, file)
    tank = TankRepository().set_photo_path(tank_id, current_user.to_core_no_relation(), photo_path)
    if tank is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tank not found")
    return tank.to_response_view()


@router.get("/{tank_id}/photo", description="Download the tank photo")
def read_photo(tank_id: int, current_user: Annotated[User, Security(get_current_user, scopes=["USER"])]):
    tank = _owned_tank_or_404(tank_id, current_user)
    if not tank.photo_path:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found")
    return FileResponse(tank.photo_path, media_type=photo_media_type(tank.photo_path))
