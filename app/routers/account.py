from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request

from app.core.client_ip import get_client_ip
from app.core.rate_limit import rate_limit_auth
from app.core.security import create_action_token, decode_action_token, hash_password
from app.core.turnstile import verify_turnstile_token
from app.models.account import (
    ActivationConfirmRequest,
    EmailRequest,
    MessageResponse,
    PasswordResetConfirmRequest,
)
from app.models.user import UserResponse
from app.repositories.user_repository import UserRepository
from app.services.email import (
    get_email_sender,
    send_account_activation_email,
    send_password_reset_email,
)

router = APIRouter(tags=["Account"])

PASSWORD_RESET_ACK = (
    "If an account exists for this email, a reset link has been sent."
)
ACCOUNT_ACTIVATION_ACK = (
    "If an account exists for this email, an activation link has been sent."
)


@router.post("/account-activations", response_model=MessageResponse)
def request_account_activation(
        request: Request,
        body: EmailRequest,
        _rate_limit: Annotated[None, Depends(rate_limit_auth)] = None,
):
    verify_turnstile_token(body.turnstileToken, get_client_ip(request))
    user = UserRepository().get_by_email(str(body.email))
    if user is not None:
        token = create_action_token("activation", user.id, user.email)
        send_account_activation_email(
            get_email_sender(),
            email=user.email,
            token=token,
        )
    return MessageResponse(detail=ACCOUNT_ACTIVATION_ACK)


@router.post("/account-activations/confirm", response_model=UserResponse)
def activate_account(body: ActivationConfirmRequest):
    payload = decode_action_token(body.token, "activation")
    user = UserRepository().get_by_id(int(payload["user_id"]))
    if user is None or user.email != payload.get("email"):
        raise HTTPException(status_code=400, detail="Invalid token")
    activated = UserRepository().mark_active(user.id)
    return UserResponse(id=activated.id, email=activated.email)


@router.post("/forgot-password", response_model=MessageResponse)
@router.post("/password-resets", response_model=MessageResponse, include_in_schema=False)
def request_password_reset(
        request: Request,
        body: EmailRequest,
        _rate_limit: Annotated[None, Depends(rate_limit_auth)] = None,
):
    """Forgot-password: always returns the same acknowledgement (no email enumeration)."""
    verify_turnstile_token(body.turnstileToken, get_client_ip(request))
    user = UserRepository().get_by_email(str(body.email))
    if user is not None:
        token = create_action_token(
            "password_reset", user.id, user.email, user.password
        )
        send_password_reset_email(
            get_email_sender(),
            email=user.email,
            user_id=user.id,
            token=token,
        )
    return MessageResponse(detail=PASSWORD_RESET_ACK)


@router.post("/recover-password", response_model=UserResponse)
@router.post("/password-resets/confirm", response_model=UserResponse, include_in_schema=False)
def reset_password(
        request: Request,
        body: PasswordResetConfirmRequest,
        _rate_limit: Annotated[None, Depends(rate_limit_auth)] = None,
):
    verify_turnstile_token(body.turnstileToken, get_client_ip(request))
    repository = UserRepository()
    user = repository.get_by_id(body.id)
    if user is None:
        raise HTTPException(status_code=400, detail="Invalid token")
    payload = decode_action_token(body.token, "password_reset", user.password)
    if int(payload["user_id"]) != user.id or payload.get("email") != user.email:
        raise HTTPException(status_code=400, detail="Invalid token")
    updated = repository.update_password(user.id, hash_password(body.password))
    return UserResponse(id=updated.id, email=updated.email)
