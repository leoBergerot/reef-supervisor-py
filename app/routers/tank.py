from typing import Annotated

from fastapi import APIRouter, File, HTTPException, Response, Security, UploadFile, status
from fastapi.responses import FileResponse

from app.core.controllers.tank import CreateTankUseCase, ListTankUseCase
from app.core.security import get_current_user
from app.models import TankResponse, TankRequest
from app.repositories import TankRepository
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


@router.patch("/{tank_id}", response_model=TankResponse, description="Rename a tank owned by the authenticated user")
def update(tank_id: int, tank_request: TankRequest,
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
