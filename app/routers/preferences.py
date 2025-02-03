from typing import Annotated

from fastapi import APIRouter, HTTPException, Security

from app.core.controllers.preference import ListPreferenceUseCase, UpdatePreferenceUseCase
from app.core.security import get_current_user
from app.models import PreferenceResponse, PreferenceRequest
from app.repositories import PreferenceRepository
from app.schemas import User

router = APIRouter(
    prefix="/preferences",
    tags=["Preferences"]
)

list_preference_controller = ListPreferenceUseCase(PreferenceRepository())


@router.get("", response_model=list[PreferenceResponse],
            description="Need authentication to read preferences and return it according to user authenticate")
def read(current_user: Annotated[User, Security(get_current_user, scopes=["USER"])]):
    return list_preference_controller.execute(current_user.to_core_no_relation())


update_preference_controller = UpdatePreferenceUseCase(PreferenceRepository())


@router.patch("/{preference_id}", response_model=PreferenceResponse,
              description="Need authentication, update preference in order to enabled or disabled parameter")
def update(preference_id: int,
           preference_request: PreferenceRequest,
           current_user: Annotated[User, Security(get_current_user, scopes=["USER"])]):
    try:
        return update_preference_controller.execute(preference_id, preference_request, current_user.to_core_no_relation())
    except Exception as e:
        error = e.args
        if 'status_code' in error[0]:
            raise HTTPException(
                status_code=error[0].get('status_code'), detail=error[0].get('detail')
            )
