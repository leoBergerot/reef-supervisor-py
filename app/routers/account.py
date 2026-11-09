from fastapi import APIRouter, HTTPException

from app.core.security import create_action_token, decode_action_token, hash_password
from app.models.account import (
    ActivationConfirmRequest,
    ActivationTokenResponse,
    EmailRequest,
    PasswordResetConfirmRequest,
    PasswordResetTokenResponse,
)
from app.models.user import UserResponse
from app.repositories.user_repository import UserRepository

router = APIRouter(tags=["Account"])


def _require_user_by_email(email: str):
    user = UserRepository().get_by_email(str(email))
    if user is None:
        raise HTTPException(status_code=404, detail="Email not registered")
    return user


@router.post("/account-activations", response_model=ActivationTokenResponse)
def request_account_activation(body: EmailRequest):
    user = _require_user_by_email(str(body.email))
    token = create_action_token("activation", user.id, user.email)
    return ActivationTokenResponse(email=user.email, token=token)


@router.post("/account-activations/confirm", response_model=UserResponse)
def activate_account(body: ActivationConfirmRequest):
    payload = decode_action_token(body.token, "activation")
    user = UserRepository().get_by_id(int(payload["user_id"]))
    if user is None or user.email != payload.get("email"):
        raise HTTPException(status_code=400, detail="Invalid token")
    activated = UserRepository().mark_active(user.id)
    return UserResponse(id=activated.id, email=activated.email)


@router.post("/password-resets", response_model=PasswordResetTokenResponse)
def request_password_reset(body: EmailRequest):
    user = _require_user_by_email(str(body.email))
    token = create_action_token("password_reset", user.id, user.email, user.password)
    return PasswordResetTokenResponse(id=user.id, email=user.email, token=token)


@router.post("/password-resets/confirm", response_model=UserResponse)
def reset_password(body: PasswordResetConfirmRequest):
    repository = UserRepository()
    user = repository.get_by_id(body.id)
    if user is None:
        raise HTTPException(status_code=400, detail="Invalid token")
    payload = decode_action_token(body.token, "password_reset", user.password)
    if int(payload["user_id"]) != user.id or payload.get("email") != user.email:
        raise HTTPException(status_code=400, detail="Invalid token")
    updated = repository.update_password(user.id, hash_password(body.password))
    return UserResponse(id=updated.id, email=updated.email)
