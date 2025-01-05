from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Security

from app.core.security import get_current_user
from app.models import PreferenceResponse, PreferenceRequest
from app.repositories import PreferenceRepository
from app.schemas import User

router = APIRouter(
    prefix="/preferences",
    tags=["Preferences"]
)


@router.get("", response_model=list[PreferenceResponse])
def read(current_user: Annotated[User, Security(get_current_user, scopes=["USER"])],
         preference_repository: Annotated[PreferenceRepository, Depends(PreferenceRepository)]):
    return [PreferenceResponse.model_validate(preference, from_attributes=True) for preference in
            preference_repository.get_by_user(current_user)]


@router.patch("/{preference_id}", response_model=PreferenceResponse,
              description="Need authentication, update preference in order to enabled or disabled parameter")
def update(preference_id: int,
           preference_request: PreferenceRequest,
           preference_repository: Annotated[PreferenceRepository, Depends(PreferenceRepository)],
           current_user: Annotated[User, Security(get_current_user, scopes=["USER"])]):
    preference = preference_repository.get_by_id_and_user(preference_id, current_user)

    if preference is None:
        raise HTTPException(
            status_code=404,
            detail="Not Found"
        )

    return PreferenceResponse.model_validate(
        preference_repository.update_persist(preference_request, preference),
        from_attributes=True
    )
