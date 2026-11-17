from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, Security

from app.core.client_ip import get_client_ip
from app.core.rate_limit import rate_limit_auth
from app.core.security import create_action_token, get_current_user, hash_password
from app.core.turnstile import verify_turnstile_token
from app.managers import UserManager
from app.models.user import UserCreateRequest, UserRequest, UserResponse
from app.repositories.user_repository import UserRepository
from app.schemas.user import User
from app.services.email import get_email_sender, send_account_activation_email

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.post("", response_model=UserResponse)
def create_user(
        request: Request,
        user: UserCreateRequest,
        user_repository: Annotated[UserRepository, Depends(UserRepository)],
        user_manager: Annotated[UserManager, Depends(UserManager)],
        _rate_limit: Annotated[None, Depends(rate_limit_auth)] = None,
):
    verify_turnstile_token(user.turnstileToken, get_client_ip(request))
    if not user_repository.is_email_unique(str(user.email)):
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = hash_password(user.password)
    new_user = User(email=user.email, password=hashed_password, is_active=False)
    new_user = user_manager.create_add_preferences_persist(new_user)

    token = create_action_token("activation", new_user.id, new_user.email)
    send_account_activation_email(
        get_email_sender(),
        email=new_user.email,
        token=token,
    )

    return UserResponse.model_validate(new_user, from_attributes=True)


@router.patch("", response_model=UserResponse)
def update_user(user: UserRequest, user_repository: Annotated[UserRepository, Depends(UserRepository)],
                current_user: Annotated[User, Security(get_current_user, scopes=["USER"])],
                user_manager: Annotated[UserManager, Depends(UserManager)]):
    if not user_repository.is_email_unique(str(user.email), current_user.id):
        raise HTTPException(status_code=400, detail="Email already registered")
    current_user = user_manager.update_persist(user, current_user)

    return UserResponse.model_validate(current_user, from_attributes=True)
